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
    def __init__(self, minio_client=None):
        """
        初始化S3数据处理器

        Args:
            minio_client: MinioClient实例，如果为None则每次操作时从MinioURL创建
        """
        self.minio_client = minio_client

    def _convert_url_string_to_minio_url(self, url_string: str) -> 'MinioURL':
        """将URL字符串转换为MinioURL对象"""
        if not isinstance(url_string, str):
            raise TypeError(f"期望字符串类型，得到: {type(url_string)}")

        if not url_string.strip():
            raise ValueError("URL字符串不能为空")

        if not url_string.startswith('s3://'):
            raise ValueError(f"不支持的URL格式，必须以's3://'开头: {url_string}")

        try:
            from evaluation_service_base.utils.minio_url import MinioURL  # 导入MinioURL类
            return MinioURL.parse_url(url_string)
        except ImportError:
            raise ImportError("需要导入MinioURL类以使用此功能")
        except Exception as e:
            raise ValueError(f"无法解析MinIO URL: {url_string}, 错误: {e}")

    def _ensure_minio_url(self, path_or_url: Union[str, 'MinioURL']) -> 'MinioURL':
        """确保返回MinioURL对象，自动转换字符串"""
        if isinstance(path_or_url, str):
            # 字符串路径，需要转换为MinioURL
            return self._convert_url_string_to_minio_url(path_or_url)
        elif hasattr(path_or_url, 'bucket_name'):
            # 已经是MinioURL对象
            return path_or_url
        else:
            raise TypeError(f"不支持的路径类型: {type(path_or_url)}")

    def _get_client_and_path(self, minio_url_or_path):
        """
        从MinioURL或路径获取客户端和路径信息 - 增强版本，自动转换字符串URL

        Args:
            minio_url_or_path: MinioURL对象或字符串路径（支持s3://格式自动转换）

        Returns:
            tuple: (client, object_name, bucket_name, minio_url_object)
        """
        # 首先尝试转换为MinioURL对象
        if isinstance(minio_url_or_path, str):
            if minio_url_or_path.startswith('s3://'):
                # s3:// 格式的字符串，转换为MinioURL
                minio_url = self._ensure_minio_url(minio_url_or_path)
            else:
                # 传统字符串路径（非s3://格式）
                if not self.minio_client:
                    raise ValueError("使用传统字符串路径时必须提供minio_client")
                return self.minio_client, minio_url_or_path, None, None
        else:
            # 假设是MinioURL对象
            minio_url = minio_url_or_path

        # 验证MinioURL
        if not minio_url.is_valid():
            raise ValueError("MinioURL缺少必要的连接信息")

        # 创建或使用客户端
        if self.minio_client:
            client = self.minio_client
        else:
            from evaluation_service_base.utils.minio_client import MinioClient  # 避免循环导入
            client = MinioClient()

        return client, minio_url.object_path, minio_url.bucket_name, minio_url

    # ======================== 增强的便捷方法 ========================

    def read_json_from_url_string(self, url_string: str) -> Dict[str, Any]:
        """便捷方法：直接从URL字符串读取JSON"""
        minio_url = self._ensure_minio_url(url_string)
        return self._read_json_from_s3(minio_url)

    def write_json_to_url_string(self, data: Dict[str, Any], url_string: str):
        """便捷方法：直接写JSON到URL字符串"""
        minio_url = self._ensure_minio_url(url_string)
        self._put_json_to_s3(data, minio_url)

    def read_hdf5_chunks_from_url_string(self, url_string: str, key: str = 'df', chunk_size: int = 100):
        """便捷方法：直接从URL字符串读取HDF5数据块"""
        minio_url = self._ensure_minio_url(url_string)
        return self.read_hdf5_chunks_from_s3(minio_url, key, chunk_size)

    def upload_hdf5_to_url_string(self, local_file: str, url_string: str):
        """便捷方法：直接上传HDF5到URL字符串"""
        minio_url = self._ensure_minio_url(url_string)
        self._put_hdf5_to_s3(local_file, minio_url)

    def download_file_from_url_string(self, url_string: str, local_path: str):
        """便捷方法：直接从URL字符串下载文件"""
        minio_url = self._ensure_minio_url(url_string)
        self._download_file_from_s3(minio_url, local_path)

    def upload_file_to_url_string(self, local_file: str, url_string: str,
                                  content_type: str = "application/octet-stream"):
        """便捷方法：直接上传文件到URL字符串"""
        minio_url = self._ensure_minio_url(url_string)
        self._put_file_to_s3(local_file, minio_url, content_type)

    # ======================== 验证和调试方法 ========================

    def validate_url_string(self, url_string: str) -> Dict[str, Any]:
        """验证URL字符串格式"""
        try:
            minio_url = self._ensure_minio_url(url_string)
            return {
                "valid": True,
                "original_url": url_string,
                "parsed_url": minio_url.build_url(),
                "components": {
                    "scheme": minio_url.scheme,
                    "host": minio_url.host,
                    "port": minio_url.port,
                    "bucket": minio_url.bucket_name,
                    "object_path": minio_url.object_path,
                },
                "is_complete": minio_url.is_valid()
            }
        except Exception as e:
            return {
                "valid": False,
                "original_url": url_string,
                "error": str(e)
            }

    def batch_validate_urls(self, url_list: List[str]) -> List[Dict[str, Any]]:
        """批量验证URL列表"""
        return [self.validate_url_string(url) for url in url_list]

    # ======================== JSON 操作 ========================
    def _read_json_from_s3(self, minio_url_or_path: Union['MinioURL', str]) -> Dict[str, Any]:
        """从S3读取JSON文件 - 支持MinioURL"""
        client, object_name, bucket_name, minio_url = self._get_client_and_path(minio_url_or_path)

        if hasattr(minio_url_or_path, 'bucket_name'):
            # 使用MinioURL
            status, response = client.download_object(minio_url)
        else:
            # 使用传统方式
            status, response = client.download_object(object_name, bucket_name)

        if not status:
            raise Exception(f"读取S3文件失败: {minio_url_or_path}")

        content = response.read()
        try:
            content_str = content.decode("utf-8")
            data = json.loads(content_str)
            return data
        except UnicodeDecodeError:
            raise Exception(f"文件 {minio_url_or_path} 不是有效的UTF-8文本文件")
        except json.JSONDecodeError as e:
            raise Exception(f"文件 {minio_url_or_path} 不是有效的JSON格式: {e}")
        finally:
            response.close()

    def _put_json_to_s3(self, json_object, minio_url_or_path: Union['MinioURL', str]):
        """写入JSON到S3 - 支持MinioURL"""
        client, object_name, bucket_name, minio_url = self._get_client_and_path(minio_url_or_path)

        try:
            json_stream = io.BytesIO(json.dumps(json_object, ensure_ascii=False, indent=2).encode('utf-8'))

            if hasattr(minio_url, 'bucket_name'):
                # 使用MinioURL
                client.put_object(minio_url, json_stream)
            else:
                # 使用传统方式
                client.put_object(object_name, json_stream, bucket_name)
        except Exception as e:
            raise Exception(f"写入S3文件失败: {minio_url_or_path}, 错误: {str(e)}")

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
    def _read_hdf5_from_s3(self, minio_url_or_path: Union['MinioURL', str]) -> Dict[str, Any]:
        """从S3读取HDF5文件并返回所有数据 - 支持MinioURL"""
        client, object_name, bucket_name, minio_url = self._get_client_and_path(minio_url_or_path)

        if hasattr(minio_url, 'bucket_name'):
            # 使用MinioURL
            status, response = client.download_object(minio_url)
        else:
            # 使用传统方式
            status, response = client.download_object(object_name, bucket_name)

        if not status:
            raise Exception(f"读取S3文件失败: {minio_url_or_path}")

        content = response.read()

        # 验证是否为HDF5文件
        if not content.startswith(b'\x89HDF'):
            raise Exception(f"文件 {minio_url_or_path} 不是HDF5格式")

        try:
            with h5py.File(io.BytesIO(content), 'r') as h5_file:
                return self._extract_all_hdf5_data(h5_file)
        except Exception as e:
            raise Exception(f"读取HDF5文件失败: {e}")
        finally:
            response.close()

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

    def read_hdf5_chunks_from_s3(self,
                                 minio_url_or_path: Union['MinioURL', str],
                                 key: str = 'df',
                                 chunk_size: int = 100) -> Generator[pd.DataFrame, None, None]:
        """从S3下载HDF5文件并分片读取 - 支持MinioURL"""
        client, object_name, bucket_name, minio_url = self._get_client_and_path(minio_url_or_path)

        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.h5', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # 下载文件到临时位置
            print(f"从S3下载HDF5文件: {minio_url_or_path}")

            if hasattr(minio_url, 'bucket_name'):
                # 使用MinioURL
                status, error = client.fget_object(minio_url, temp_path)
            else:
                # 使用传统方式
                status, error = client.fget_object(object_name, temp_path, bucket_name)

            if not status:
                raise Exception(f"从S3下载文件失败: {minio_url_or_path}, 错误: {error}")

            # 分片读取
            yield from self.read_hdf_chunks(temp_path, key, chunk_size)

        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                print(f"已清理临时文件: {temp_path}")

    def _put_hdf5_to_s3(self,
                        file_path: str,
                        minio_url_or_path: Union['MinioURL', str]):
        """上传HDF5文件到S3 - 支持MinioURL"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"本地文件不存在: {file_path}")

        client, object_name, bucket_name, minio_url = self._get_client_and_path(minio_url_or_path)

        try:
            if hasattr(minio_url, 'bucket_name'):
                # 使用MinioURL
                client.fput_object(
                    minio_url,
                    file_path=file_path,
                    content_type="application/x-hdf5"
                )
            else:
                # 使用传统方式
                client.fput_object(
                    object_name,
                    file_path=file_path,
                    bucket_name=bucket_name,
                    content_type="application/x-hdf5"
                )
            print(f"HDF5文件上传成功: {file_path} -> {minio_url_or_path}")
        except Exception as e:
            raise Exception(f"上传HDF5文件到S3失败: {minio_url_or_path}, 错误: {str(e)}")

    # ======================== 通用文件操作 ========================
    def _put_detail_to_s3(self,
                          file_path: str,
                          minio_url_or_path: Union['MinioURL', str],
                          content_type: str = "application/json"):
        """写入文件到S3 - 支持MinioURL"""
        self._put_file_to_s3(file_path, minio_url_or_path, content_type)

    def _put_file_to_s3(self,
                        file_path: str,
                        minio_url_or_path: Union['MinioURL', str],
                        content_type: str = "application/json"):
        """写入文件到S3 - 支持MinioURL"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"本地文件不存在: {file_path}")

        client, object_name, bucket_name, minio_url = self._get_client_and_path(minio_url_or_path)

        try:
            if hasattr(minio_url_or_path, 'bucket_name'):
                # 使用MinioURL
                client.fput_object(
                    minio_url,
                    file_path=file_path,
                    content_type=content_type
                )
            else:
                # 使用传统方式
                client.fput_object(
                    minio_url,
                    file_path=file_path,
                    bucket_name=bucket_name,
                    content_type=content_type
                )
            print(f"文件上传成功: {file_path} -> {minio_url_or_path}")
        except Exception as e:
            raise Exception(f"写入S3文件失败: {minio_url_or_path}, 错误: {str(e)}")

    def _download_file_from_s3(self,
                               minio_url_or_path: Union['MinioURL', str],
                               local_path: str):
        """从S3下载文件到本地 - 支持MinioURL"""
        client, object_name, bucket_name, minio_url = self._get_client_and_path(minio_url_or_path)

        try:
            # 创建本地目录（如果不存在）
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            if hasattr(minio_url, 'bucket_name'):
                # 使用MinioURL
                status, error = client.fget_object(minio_url, local_path)
            else:
                # 使用传统方式
                status, error = client.fget_object(object_name, local_path, bucket_name)

            if not status:
                raise Exception(f"下载失败: {error}")
            print(f"文件下载成功: {minio_url_or_path} -> {local_path}")
        except Exception as e:
            raise Exception(f"从S3下载文件失败: {minio_url_or_path}, 错误: {str(e)}")

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

    # ======================== 新增便捷方法 ========================
    def read_json_from_url(self, minio_url: 'MinioURL') -> Dict[str, Any]:
        """便捷方法：直接从MinioURL读取JSON"""
        return self._read_json_from_s3(minio_url)

    def write_json_to_url(self, data: Dict[str, Any], minio_url: 'MinioURL'):
        """便捷方法：直接写JSON到MinioURL"""
        self._put_json_to_s3(data, minio_url)

    def read_hdf5_from_url(self, minio_url: 'MinioURL') -> Dict[str, Any]:
        """便捷方法：直接从MinioURL读取HDF5"""
        return self._read_hdf5_from_s3(minio_url)

    def upload_hdf5_to_url(self, local_file: str, minio_url: 'MinioURL'):
        """便捷方法：直接上传HDF5到MinioURL"""
        self._put_hdf5_to_s3(local_file, minio_url)

    def download_file_from_url(self, minio_url: 'MinioURL', local_path: str):
        """便捷方法：直接从MinioURL下载文件"""
        self._download_file_from_s3(minio_url, local_path)

    def upload_file_to_url(self, local_file: str, minio_url: 'MinioURL',
                           content_type: str = "application/octet-stream"):
        """便捷方法：直接上传文件到MinioURL"""
        self._put_file_to_s3(local_file, minio_url, content_type)


# 使用示例
if __name__ == '__main__':
    from minio_url import MinioURL
    from minio_client import MinioClient, MinioConfig

    # 方式1: 使用MinioURL (推荐)
    minio_url = MinioURL.parse_url("s3://mykey:mysecret@localhost:9000/my-bucket/data/test.json")

    # 创建处理器（不需要预设客户端）
    handler = S3DataHandler()

    # JSON操作
    test_data = {"name": "test", "value": 123}
    handler.write_json_to_url(test_data, minio_url)
    loaded_data = handler.read_json_from_url(minio_url)
    print(f"读取的JSON数据: {loaded_data}")

    # 文件操作
    handler.upload_file_to_url("local_file.txt", minio_url)
    handler.download_file_from_url(minio_url, "downloaded_file.txt")

    # HDF5操作
    hdf5_url = MinioURL.parse_url("s3://mykey:mysecret@localhost:9000/my-bucket/data/data.h5")
    handler.upload_hdf5_to_url("local_data.h5", hdf5_url)

    # 分片读取HDF5
    for chunk in handler.read_hdf5_chunks_from_s3(hdf5_url, key='df', chunk_size=1000):
        print(f"处理数据块，形状: {chunk.shape}")
        # 处理数据块...

    # 方式2: 传统方式（向后兼容）
    config = MinioConfig(
        endpoint="localhost:9000",
        access_key="mykey",
        secret_key="mysecret"
    )
    client = MinioClient(config)
    handler_traditional = S3DataHandler(client)

    # 传统方式仍然有效
    data = handler_traditional._read_json_from_s3("data/test.json")
    print(f"传统方式读取: {data}")
