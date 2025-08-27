import json
import io
import traceback

import pandas as pd
import h5py
from typing import Dict, Any, Generator, Optional, Union, List
import tempfile
import os

from liblogging import logger



class S3DataHandler:
    def __init__(self, minio_client):
        self.minio_client = minio_client

    # ======================== JSON 操作 ========================
    def _read_json_from_s3(self, s3_path: str) -> Dict[str, Any]:
        """从S3读取JSON文件 - 通用实现"""
        status, response = self.minio_client.download_object(s3_path)
        if not status:
            raise Exception(f"读取S3文件失败: {s3_path}")

        content = response.read()
        try:
            content_str = content.decode("utf-8")
            data = json.loads(content_str)
            return data
        except UnicodeDecodeError:
            raise Exception(f"文件 {s3_path} 不是有效的UTF-8文本文件")
        except json.JSONDecodeError as e:
            raise Exception(f"文件 {s3_path} 不是有效的JSON格式: {e}")

    def _put_json_to_s3(self, json_object, s3_path: str):
        """写入JSON到S3 - 通用实现"""
        try:
            json_stream = io.BytesIO(json.dumps(json_object, ensure_ascii=False, indent=2).encode('utf-8'))
            self.minio_client.put_object(s3_path, json_stream)
        except Exception as e:
            raise Exception(f"写入S3文件失败: {s3_path}, 错误: {str(e)}")

    # ======================== HDF5 本地操作 ========================
    def read_hdf_chunks(self, file_path: str, key: str = 'df', chunk_size: int = 100) -> Generator[
        pd.DataFrame, None, None]:
        """
        分片读取 HDF5 文件，以生成器方式返回每片数据。

        Args:
            file_path: HDF5 文件路径
            key: HDF5 中存储 DataFrame 的键
            chunk_size: 每次读取的行数

        Returns:
            生成器，每次返回一个 DataFrame 片段
        """
        if chunk_size <= 0:
            raise ValueError("chunk_size 必须大于 0")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"HDF5文件不存在: {file_path}")

        with pd.HDFStore(file_path, mode='r') as store:
            # 检查是否存在该 key
            if key not in store:
                available_keys = list(store.keys())
                raise KeyError(f"HDF5 文件中未找到键: {key}，可用键: {available_keys}")

            storer = store.get_storer(key)
            # 获取总量
            total_rows = storer.nrows
            print(f"总行数: {total_rows}, 每批次: {chunk_size}")

            start = 0
            batch_num = 0
            while start < total_rows:
                end = min(start + chunk_size, total_rows)
                batch_num += 1
                print(f"读取批次 {batch_num}: 行 {start}-{end - 1}")
                yield store.select(key, start=start, stop=end)
                start = end

    def append_to_hdf5(self, df: pd.DataFrame, file_path: str, key: str = 'df'):
        """将DataFrame数据存入HDF5文件中
        Args:
            df: 待追加的DataFrame数据
            file_path: HDF5文件路径
            key: HDF5文件存储键
        """
        if df.empty:
            print("警告: DataFrame为空，跳过写入")
            return

        def safe_json_dumps(x):
            # 首先检查None
            if x is None:
                return None

            # 安全检查是否为NaN
            try:
                if pd.isna(x):
                    return None
            except (TypeError, ValueError):
                # 如果pd.isna()失败，继续处理
                pass

            # 如果已经是基本类型，直接返回
            if isinstance(x, (str, int, float, bool)):
                return x

            # 尝试JSON序列化
            try:
                return json.dumps(x, ensure_ascii=False)
            except (TypeError, ValueError):
                return str(x)

        df = df.copy()  # 避免修改原始数据

        # 处理object类型列
        object_cols = df.select_dtypes(include='object').columns
        if len(object_cols) > 0:
            print(f"处理object类型列: {list(object_cols)}")
            for col in object_cols:
                df[col] = df[col].apply(safe_json_dumps)

        # 创建目录（如果不存在）
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        try:
            with pd.HDFStore(file_path, mode='a') as store:
                if key in store:
                    # 已存在数据
                    store.append(key, df, format='table', data_columns=True)
                else:
                    store.put(key, df, format='table', data_columns=True)

        except ValueError as e:
            if "column has a limit of" in str(e):
                logger.warning(f"检测到列宽不足，将执行动态扩展操作... 错误: {e}")
                # 读取旧数据
                df_old = pd.DataFrame()
                with pd.HDFStore(file_path, mode='a') as store_read:
                    df_old = store_read.get(key)
                # 合并新旧数据
                df_combined = pd.concat([df_old, df], ignore_index=True)
                # 创建副本
                backup_path = file_path + '.bak'
                os.rename(file_path, backup_path)
                # 尝试写入新数据
                try:
                    with pd.HDFStore(file_path, mode='w') as store_write:
                        store_write.put(key, df_combined, format='table', data_columns=True)

                    logger.info("动态扩展成功，数据已重写。")
                    # 成功后删除备份
                    os.remove(backup_path)
                except Exception as write_e:
                    # 如果重写失败，恢复备份
                    logger.error(f"重写扩容HDF5文件失败: {write_e}。正在从备份恢复...")
                    os.rename(backup_path, file_path)
                    raise write_e
            else:
                raise e
        except Exception as e:
            logger.error(f"将数据追加到HDF5文件失败: {str(e)}\n{traceback.format_exc()}")

    # ======================== HDF5 S3 操作 ========================
    def _read_hdf5_from_s3(self, s3_path: str) -> Dict[str, Any]:
        """从S3读取HDF5文件并返回所有数据"""
        status, response = self.minio_client.download_object(s3_path)
        if not status:
            raise Exception(f"读取S3文件失败: {s3_path}")

        content = response.read()

        # 验证是否为HDF5文件
        if not content.startswith(b'\x89HDF'):
            raise Exception(f"文件 {s3_path} 不是HDF5格式")

        try:
            with h5py.File(io.BytesIO(content), 'r') as h5_file:
                return self._extract_all_hdf5_data(h5_file)
        except Exception as e:
            raise Exception(f"读取HDF5文件失败: {e}")

    def _extract_all_hdf5_data(self, h5_file) -> Dict[str, Any]:
        """提取HDF5文件的所有数据"""
        result = {
            'datasets': {},
            'groups': {},
            'attributes': dict(h5_file.attrs),
            'structure': []
        }

        def extract_item(name, obj):
            result['structure'].append(name)
            if isinstance(obj, h5py.Dataset):
                # 对于大数据集，只返回元信息
                if obj.size > 100000:  # 超过10万个元素
                    data_info = f"Large dataset: shape {obj.shape}, size {obj.size}"
                else:
                    data_info = obj[...].tolist()

                result['datasets'][name] = {
                    'data': data_info,
                    'shape': obj.shape,
                    'dtype': str(obj.dtype),
                    'size': obj.size,
                    'attributes': dict(obj.attrs)
                }
            elif isinstance(obj, h5py.Group):
                result['groups'][name] = {
                    'attributes': dict(obj.attrs),
                    'keys': list(obj.keys())
                }

        h5_file.visititems(extract_item)
        return result

    def read_hdf5_chunks_from_s3(self, s3_path: str, key: str = 'df', chunk_size: int = 100) -> Generator[
        pd.DataFrame, None, None]:
        """从S3下载HDF5文件并分片读取"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.h5', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # 下载文件到临时位置
            print(f"从S3下载HDF5文件: {s3_path}")
            status = self.minio_client.fget_object(s3_path, temp_path)
            if not status:
                raise Exception(f"从S3下载文件失败: {s3_path}")

            # 分片读取
            yield from self.read_hdf_chunks(temp_path, key, chunk_size)

        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                print(f"已清理临时文件: {temp_path}")

    def _put_hdf5_to_s3(self, file_path: str, s3_path: str):
        """上传HDF5文件到S3"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"本地文件不存在: {file_path}")

        try:
            self.minio_client.fput_object(
                s3_path,
                file_path=file_path,
                content_type="application/x-hdf5"
            )
            print(f"HDF5文件上传成功: {file_path} -> {s3_path}")
        except Exception as e:
            raise Exception(f"上传HDF5文件到S3失败: {s3_path}, 错误: {str(e)}")

    # ======================== 通用文件操作 ========================
    def _put_detail_to_s3(self, file_path: str, s3_path: str, content_type: str = "application/json"):
        """写入文件到S3 - 通用实现"""
        self._put_file_to_s3(file_path, s3_path, content_type)

    def _put_file_to_s3(self, file_path: str, s3_path: str, content_type: str = "application/json"):
        """写入文件到S3 - 通用实现"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"本地文件不存在: {file_path}")

        try:
            self.minio_client.fput_object(
                s3_path,
                file_path=file_path,
                content_type=content_type
            )
            print(f"文件上传成功: {file_path} -> {s3_path}")
        except Exception as e:
            raise Exception(f"写入S3文件失败: {s3_path}, 错误: {str(e)}")

    def _download_file_from_s3(self, s3_path: str, local_path: str):
        """从S3下载文件到本地"""
        try:
            # 创建本地目录（如果不存在）
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            status = self.minio_client.fget_object(s3_path, local_path)
            if not status:
                raise Exception(f"下载失败")
            print(f"文件下载成功: {s3_path} -> {local_path}")
        except Exception as e:
            raise Exception(f"从S3下载文件失败: {s3_path}, 错误: {str(e)}")

    # ======================== 实用方法 ========================
    def get_file_info_from_s3(self, s3_path: str) -> Dict[str, Any]:
        """获取S3文件信息"""
        try:
            status, response = self.minio_client.download_object(s3_path)
            if not status:
                raise Exception(f"文件不存在: {s3_path}")

            content = response.read()
            file_info = {
                'size': len(content),
                'type': 'unknown'
            }

            # 检测文件类型
            if content.startswith(b'\x89HDF'):
                file_info['type'] = 'hdf5'
            elif content.strip().startswith(b'{') or content.strip().startswith(b'['):
                file_info['type'] = 'json'
            elif b',' in content and b'\n' in content:
                file_info['type'] = 'csv'

            return file_info
        except Exception as e:
            raise Exception(f"获取文件信息失败: {s3_path}, 错误: {str(e)}")

    def list_hdf5_keys(self, file_path: str) -> List[str]:
        """列出HDF5文件中的所有键"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"HDF5文件不存在: {file_path}")

        with pd.HDFStore(file_path, mode='r') as store:
            return list(store.keys())

    def get_hdf5_info(self, file_path: str, key: str = None) -> Dict[str, Any]:
        """获取HDF5文件信息"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"HDF5文件不存在: {file_path}")

        info = {'keys': [], 'details': {}}

        with pd.HDFStore(file_path, mode='r') as store:
            info['keys'] = list(store.keys())

            if key:
                if key in store:
                    storer = store.get_storer(key)
                    info['details'][key] = {
                        'nrows': storer.nrows,
                        'ncols': len(storer.attrs.values_axes[0]),
                        'columns': list(storer.attrs.values_axes[0])
                    }
                else:
                    raise KeyError(f"键 '{key}' 不存在于HDF5文件中")
            else:
                # 获取所有键的信息
                for k in info['keys']:
                    storer = store.get_storer(k)
                    info['details'][k] = {
                        'nrows': storer.nrows,
                        'ncols': len(storer.attrs.values_axes[0]),
                        'columns': list(storer.attrs.values_axes[0])
                    }

        return info
