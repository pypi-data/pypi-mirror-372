from typing import Optional, BinaryIO, Union
import json
import os
from minio import Minio, S3Error
from minio.commonconfig import CopySource
from dataclasses import dataclass


@dataclass
class MinioConfig:
    """Minio配置类"""
    endpoint: str
    access_key: str
    secret_key: str
    secure: bool = False
    cert_check: bool = False
    default_bucket: str = "default"
    forwarding_address: Optional[str] = None


class MinioClient:
    """支持MinioURL的MinIO客户端"""

    def __init__(self, config: Optional[MinioConfig] = None):
        self.config = config
        if config:
            self.client = Minio(
                endpoint=config.endpoint,
                access_key=config.access_key,
                secret_key=config.secret_key,
                secure=config.secure,
                cert_check=config.cert_check
            )
        else:
            self.client = None

    def _get_client_from_url(self, minio_url) -> Minio:
        """从MinioURL创建客户端连接"""
        if not minio_url.is_valid():
            raise ValueError("MinioURL缺少必要的连接信息")

        return Minio(
            endpoint=minio_url.get_endpoint(),
            access_key=minio_url.access_key,
            secret_key=minio_url.secret_key,
            secure=minio_url.secure,
            cert_check=False
        )
    def _resolve_params(self, minio_url_or_params):
        """解析参数，支持MinioURL或传统参数"""
        if hasattr(minio_url_or_params, 'bucket_name'):  # 是MinioURL对象
            minio_url = minio_url_or_params
            client = self._get_client_from_url(minio_url)
            bucket_name = minio_url.bucket_name
            object_name = minio_url.object_path
            return client, bucket_name, object_name
        else:
            # 传统方式，使用默认客户端
            if not self.client:
                raise ValueError("需要提供MinioURL对象或初始化默认配置")
            return self.client, None, None

    def is_bucket_exists(self,
                         minio_url_or_bucket: Union['MinioURL', str, None] = None,
                         auto_create: bool = True):
        """验证桶是否存在

        Args:
            minio_url_or_bucket: MinioURL对象或桶名称
            auto_create: 是否自动创建不存在的桶
        """
        if hasattr(minio_url_or_bucket, 'bucket_name'):
            # MinioURL对象
            minio_url = minio_url_or_bucket
            client = self._get_client_from_url(minio_url)
            bucket_name = minio_url.bucket_name
        else:
            # 传统方式
            client = self.client
            bucket_name = minio_url_or_bucket or self.config.default_bucket

        try:
            if not client.bucket_exists(bucket_name):
                print(f"s3 object storage bucket {bucket_name} does not exist")
                if auto_create:
                    client.make_bucket(bucket_name)
                    print(f"s3 object storage bucket {bucket_name} created")
                    return True, None
                return False, "桶不存在"
        except S3Error as e:
            print(f"s3 object storage check bucket error: {e}")
            return False, "未查找到指定桶对象"
        return True, None

    def fput_object(self,
                    minio_url_or_object: Union['MinioURL', str],
                    file_path: Optional[str] = None,
                    bucket_name: Optional[str] = None,
                    content_type: str = "application/json"):
        """上传本地文件到S3对象存储

        Args:
            minio_url_or_object: MinioURL对象或对象名称
            file_path: 本地文件路径
            bucket_name: 桶名称（使用MinioURL时忽略）
            content_type: 内容类型
        """
        if hasattr(minio_url_or_object, 'bucket_name'):
            # MinioURL对象
            minio_url = minio_url_or_object
            client = self._get_client_from_url(minio_url)
            bucket_name = minio_url.bucket_name
            object_name = minio_url.object_path
            if not file_path:
                raise ValueError("使用MinioURL时必须提供file_path参数")
        else:
            # 传统方式
            client = self.client
            object_name = minio_url_or_object
            bucket_name = bucket_name or self.config.default_bucket

        try:
            client.fput_object(bucket_name, object_name, file_path, content_type)
            print(f"s3 object storage bucket {bucket_name} uploaded object {object_name}")
        except S3Error as e:
            print(f"s3 object storage upload object [{object_name}] error: {e}")
            return False, "对象文件上传失败"
        return True, None

    def fget_object(self,
                    minio_url_or_object: Union['MinioURL', str],
                    file_path: Optional[str] = None,
                    bucket_name: Optional[str] = None):
        """从S3对象存储下载文件到本地

        Args:
            minio_url_or_object: MinioURL对象或对象名称
            file_path: 本地文件保存路径
            bucket_name: 桶名称（使用MinioURL时忽略）
        """
        if hasattr(minio_url_or_object, 'bucket_name'):
            # MinioURL对象
            minio_url = minio_url_or_object
            client = self._get_client_from_url(minio_url)
            bucket_name = minio_url.bucket_name
            object_name = minio_url.object_path
            if not file_path:
                raise ValueError("使用MinioURL时必须提供file_path参数")
        else:
            # 传统方式
            client = self.client
            object_name = minio_url_or_object
            bucket_name = bucket_name or self.config.default_bucket

        try:
            # 确保本地目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            client.fget_object(bucket_name, object_name, file_path)
            print(f"s3 object storage bucket {bucket_name} downloaded object {object_name} to {file_path}")
        except S3Error as e:
            print(f"s3 object storage download object [{object_name}] error: {e}")
            return False, "对象文件下载失败"
        return True, None

    def put_object(self,
                   minio_url_or_object: Union['MinioURL', str],
                   object_content: Optional[BinaryIO] = None,
                   bucket_name: Optional[str] = None,
                   object_length: int = -1,
                   part_size: int = 5 * 1024 * 1024):
        """上传文件流到s3对象存储

        Args:
            minio_url_or_object: MinioURL对象或对象名称
            object_content: 数据流对象
            bucket_name: 桶名称（使用MinioURL时忽略）
            object_length: 数据流大小 (未知大小时使用-1)
            part_size: 分片大小 (数据流大小为-1时, 分片大小不能小于5MB)
        """
        if hasattr(minio_url_or_object, 'bucket_name'):
            # MinioURL对象
            minio_url = minio_url_or_object
            client = self._get_client_from_url(minio_url)
            bucket_name = minio_url.bucket_name
            object_name = minio_url.object_path
            if object_content is None:
                raise ValueError("使用MinioURL时必须提供object_content参数")
        else:
            # 传统方式
            client = self.client
            object_name = minio_url_or_object
            bucket_name = bucket_name or self.config.default_bucket

        try:
            client.put_object(bucket_name, object_name, object_content,
                              length=object_length, part_size=part_size)
            print(f"s3 object storage bucket {bucket_name} uploaded object {object_name}")
        except S3Error as e:
            print(f"s3 object storage upload object [{object_name}] error: {e}")
            return False, "对象数据流上传失败"
        return True, None

    def download_object(self,
                        minio_url_or_object: Union['MinioURL', str],
                        bucket_name: Optional[str] = None):
        """从s3对象存储获取对象数据流

        Args:
            minio_url_or_object: MinioURL对象或对象名称
            bucket_name: 桶名称（使用MinioURL时忽略）
        """
        if hasattr(minio_url_or_object, 'bucket_name'):
            # MinioURL对象
            minio_url = minio_url_or_object
            client = self._get_client_from_url(minio_url)
            bucket_name = minio_url.bucket_name
            object_name = minio_url.object_path
        else:
            # 传统方式
            client = self.client
            object_name = minio_url_or_object
            bucket_name = bucket_name or self.config.default_bucket

        try:
            s3_object = client.get_object(bucket_name, object_name)
        except S3Error as e:
            print(f"s3 object storage get object [{object_name}] error: {e}")
            return False, "对象数据流下载失败"
        return True, s3_object

    def list_object(self,
                    minio_url_or_prefix: Union['MinioURL', str, None] = None,
                    bucket_name: Optional[str] = None,
                    recursive: bool = True):
        """匹配获取对象列表

        Args:
            minio_url_or_prefix: MinioURL对象或对象前缀
            bucket_name: 桶名称（使用MinioURL时忽略）
            recursive: 是否递归查询
        """
        if hasattr(minio_url_or_prefix, 'bucket_name'):
            # MinioURL对象
            minio_url = minio_url_or_prefix
            client = self._get_client_from_url(minio_url)
            bucket_name = minio_url.bucket_name
            prefix = minio_url.object_path or ""
        else:
            # 传统方式
            client = self.client
            prefix = minio_url_or_prefix
            bucket_name = bucket_name or self.config.default_bucket

        object_list = []
        try:
            s3_objects = client.list_objects(bucket_name, prefix=prefix, recursive=recursive)
            for _file in s3_objects:
                object_list.append(_file)
        except S3Error as e:
            print(f"s3 object storage get object [{prefix}] error: {e}")
            return False, "对象列表获取失败"
        return True, object_list

    def state_object(self,
                     minio_url_or_object: Union['MinioURL', str],
                     bucket_name: Optional[str] = None):
        """获取对象存储状态信息

        Args:
            minio_url_or_object: MinioURL对象或对象名称
            bucket_name: 桶名称（使用MinioURL时忽略）
        """
        if hasattr(minio_url_or_object, 'bucket_name'):
            # MinioURL对象
            minio_url = minio_url_or_object
            client = self._get_client_from_url(minio_url)
            bucket_name = minio_url.bucket_name
            object_name = minio_url.object_path
        else:
            # 传统方式
            client = self.client
            object_name = minio_url_or_object
            bucket_name = bucket_name or self.config.default_bucket

        try:
            s3_object = client.stat_object(bucket_name, object_name)
        except S3Error as e:
            print(f"s3 object storage get object [{object_name}] error: {e}")
            return False, "获取对象存储信息失败"
        return True, s3_object

    def delete_object(self,
                      minio_url_or_object: Union['MinioURL', str],
                      bucket_name: Optional[str] = None):
        """从s3对象存储删除对象

        Args:
            minio_url_or_object: MinioURL对象或对象名称
            bucket_name: 桶名称（使用MinioURL时忽略）
        """
        if hasattr(minio_url_or_object, 'bucket_name'):
            # MinioURL对象
            minio_url = minio_url_or_object
            client = self._get_client_from_url(minio_url)
            bucket_name = minio_url.bucket_name
            object_name = minio_url.object_path
        else:
            # 传统方式
            client = self.client
            object_name = minio_url_or_object
            bucket_name = bucket_name or self.config.default_bucket

        try:
            client.remove_object(bucket_name, object_name)
            print(f"s3 object storage deleted object {object_name}")
            return True
        except S3Error as e:
            print(f"s3 object storage delete object [{object_name}] error: {e}")
            return False

    def object_exists(self,
                      minio_url_or_object: Union['MinioURL', str],
                      bucket_name: Optional[str] = None):
        """检查对象是否存在

        Args:
            minio_url_or_object: MinioURL对象或对象名称
            bucket_name: 桶名称（使用MinioURL时忽略）
        """
        if hasattr(minio_url_or_object, 'bucket_name'):
            # MinioURL对象
            minio_url = minio_url_or_object
            client = self._get_client_from_url(minio_url)
            bucket_name = minio_url.bucket_name
            object_name = minio_url.object_path
        else:
            # 传统方式
            client = self.client
            object_name = minio_url_or_object
            bucket_name = bucket_name or self.config.default_bucket

        try:
            client.stat_object(bucket_name, object_name)
            return True
        except S3Error:
            return False

    def get_object_size(self,
                        minio_url_or_object: Union['MinioURL', str],
                        bucket_name: Optional[str] = None):
        """获取对象大小

        Args:
            minio_url_or_object: MinioURL对象或对象名称
            bucket_name: 桶名称（使用MinioURL时忽略）
        """
        if hasattr(minio_url_or_object, 'bucket_name'):
            # MinioURL对象
            minio_url = minio_url_or_object
            client = self._get_client_from_url(minio_url)
            bucket_name = minio_url.bucket_name
            object_name = minio_url.object_path
        else:
            # 传统方式
            client = self.client
            object_name = minio_url_or_object
            bucket_name = bucket_name or self.config.default_bucket

        try:
            stat_info = client.stat_object(bucket_name, object_name)
            return True, stat_info.size
        except S3Error as e:
            print(f"s3 object storage get size [{object_name}] error: {e}")
            return False, "获取对象大小失败"

    def download_json(self, minio_url_or_object: Union['MinioURL', str],
                      bucket_name: Optional[str] = None):
        """便捷方法：下载并解析JSON对象"""
        success, response = self.download_object(minio_url_or_object, bucket_name)
        if not success:
            return False, response

        try:
            content = response.read()
            content_str = content.decode("utf-8")
            data = json.loads(content_str)
            return True, data
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            return False, f"JSON解析失败: {e}"
        finally:
            response.close()

    def __del__(self):
        pass


# 使用示例
if __name__ == '__main__':
    from evaluation_service_base.utils.minio_url import MinioURL  # 假设MinioURL类在minio_url.py文件中

    # 方式1: 使用MinioURL
    minio_url = MinioURL.parse_url("s3://mykey:mysecret@localhost:9000/my-bucket/data/test.json")

    # 创建客户端（不需要配置，因为会从URL中获取）
    client = MinioClient()

    # 检查桶是否存在
    success, error = client.is_bucket_exists(minio_url)
    print(f"桶检查结果: {success}, 错误: {error}")

    # 上传文件
    success, error = client.fput_object(minio_url, file_path="local/path/test.json")
    print(f"上传结果: {success}, 错误: {error}")

    # 下载文件
    success, error = client.fget_object(minio_url, file_path="download/path/test.json")
    print(f"下载结果: {success}, 错误: {error}")

    # 获取对象流
    success, response = client.download_object(minio_url)
    if success:
        content = response.read().decode("utf-8")
        print(f"对象内容: {content[:100]}...")
        response.close()

    # 下载JSON（便捷方法）
    success, data = client.download_json(minio_url)
    if success:
        print(f"JSON数据: {data}")

    # 方式2: 传统方式（向后兼容）
    config = MinioConfig(
        endpoint="localhost:9000",
        access_key="mykey",
        secret_key="mysecret"
    )
    client_traditional = MinioClient(config)

    # 传统调用方式仍然有效
    success, response = client_traditional.download_object("data/test.json", bucket_name="my-bucket")