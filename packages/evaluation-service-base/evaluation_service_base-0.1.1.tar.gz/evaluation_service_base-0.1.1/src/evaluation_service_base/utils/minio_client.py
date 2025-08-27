
from typing import Optional, BinaryIO
import json
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
    def __init__(self, config: MinioConfig):
        """
        初始化MinioClient
        Args:
            config: Minio配置对象
        """
        self.config = config
        try:
            self.client = Minio(
                endpoint=config.endpoint,
                access_key=config.access_key,
                secret_key=config.secret_key,
                secure=config.secure,
                cert_check=config.cert_check,
            )
        except Exception as e:
            print(f"s3 object storage connect error: {e}")
            raise e

    def is_bucket_exists(self, bucket_name: Optional[str] = None, auto_create: bool = True):
        """验证桶是否存在"""
        if bucket_name is None:
            bucket_name = self.config.default_bucket

        try:
            if not self.client.bucket_exists(bucket_name):
                print(f"s3 object storage bucket {bucket_name} does not exist")
                if auto_create:
                    self.client.make_bucket(bucket_name)
                    print(f"s3 object storage bucket {bucket_name} created")
        except S3Error as e:
            print(f"s3 object storage check bucket error: {e}")
            return False, "未查找到指定桶对象"
        return True, None

    def fput_object(
            self,
            object_name: str,
            file_path: str,
            bucket_name: Optional[str] = None,
            content_type: str = "application/json"
    ):
        """上传本地文件到S3对象存储"""
        if bucket_name is None:
            bucket_name = self.config.default_bucket

        try:
            self.client.fput_object(bucket_name, object_name, file_path, content_type)
            print(f"s3 object storage bucket {bucket_name} uploaded object {object_name}")
        except S3Error as e:
            print(f"s3 object storage upload object [{object_name}] error: {e}")
            return False, "对象文件上传失败"
        return True, None

    def fget_object(
            self,
            object_name: str,
            file_path: str,
            bucket_name: Optional[str] = None,
    ):
        """
        从S3对象存储下载文件到本地
        Args:
            object_name: 对象名称
            file_path: 本地文件保存路径
            bucket_name: 桶名称

        Returns:
            tuple: (成功标志, 错误信息)
        """
        if bucket_name is None:
            bucket_name = self.config.default_bucket

        try:
            # 确保本地目录存在
            import os
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            self.client.fget_object(bucket_name, object_name, file_path)
            print(f"s3 object storage bucket {bucket_name} downloaded object {object_name} to {file_path}")
        except S3Error as e:
            print(f"s3 object storage download object [{object_name}] error: {e}")
            return False, "对象文件下载失败"
        return True, None

    def put_object(
            self,
            object_name: str,
            object_content: BinaryIO,
            bucket_name: Optional[str] = None,
            object_length: int = -1,
            part_size: int = 5 * 1024 * 1024
    ):
        """
        上传文件流到s3对象存储
        Args:
            object_name: 对象名称
            object_content: 数据流对象
            bucket_name: 桶名称
            object_length: 数据流大小 (未知大小时使用-1)
            part_size: 分片大小 (数据流大小为-1时, 分片大小不能小于5MB)

        Returns:

        """
        if bucket_name is None:
            bucket_name = self.config.default_bucket
        try:
            self.client.put_object(bucket_name, object_name, object_content, length=object_length, part_size=part_size)
            print(f"s3 object storage bucket {bucket_name} uploaded object {object_name}")
        except S3Error as e:
            print(f"s3 object storage upload object [{object_name}] error: {e}")
            return False, "对象数据流上传失败"
        return True, None

    def download_object(
            self,
            object_name: str,
            bucket_name: Optional[str] = None,
    ):
        """
        从s3对象存储获取对象数据流
        Args:
            bucket_name: 桶名称
            object_name: 对象名称

        Returns:

        """
        if bucket_name is None:
            bucket_name = self.config.default_bucket
        try:
            s3_object = self.client.get_object(bucket_name, object_name)
        except S3Error as e:
            print(f"s3 object storage get object [{object_name}] error: {e}")
            return False, "对象数据流下载失败"
        return True, s3_object

    def list_object(
            self,
            prefix: Optional[str],
            bucket_name: Optional[str] = None,
            recursive=True
    ):
        """
        匹配获取对象列表
        Args:
            bucket_name: 桶名称
            prefix: 对象前缀
            recursive: 是否递归查询

        Returns:

        """
        if bucket_name is None:
            bucket_name = self.config.default_bucket
        object_list = []
        try:
            s3_object = self.client.list_objects(bucket_name, prefix=prefix, recursive=recursive)
            for _file in s3_object:
                object_list.append(_file)
        except S3Error as e:
            print(f"s3 object storage get object [{prefix}] error: {e}")
            return False, "对象列表获取失败"
        return True, object_list

    def state_object(
            self,
            object_name: str,
            bucket_name: Optional[str] = None,
    ):
        """
        获取对象存储状态信息
        Args:
            bucket_name: 桶名称
            object_name: 对象名称

        Returns:

        """
        if bucket_name is None:
            bucket_name = self.config.default_bucket
        try:
            s3_object = self.client.stat_object(bucket_name, object_name)
        except S3Error as e:
            print(f"s3 object storage get object [{object_name}] error: {e}")
            return False, "获取对象存储信息失败"
        return True, s3_object


    def delete_object(
            self,
            object_name: str,
            bucket_name: Optional[str] = None
    ):
        """
        从s3对象存储删除对象
        Args:
            bucket_name: 桶名称
            object_name: 对象名称

        Returns:
            bool: 删除是否成功
        """
        if bucket_name is None:
            bucket_name = self.config.default_bucket
        try:
            self.client.remove_object(bucket_name, object_name)
            print(f"s3 object storage deleted object {object_name}")
            return True
        except S3Error as e:
            print(f"s3 object storage delete object [{object_name}] error: {e}")
            return False


    def object_exists(
            self,
            object_name: str,
            bucket_name: Optional[str] = None
    ):
        """
        检查对象是否存在
        Args:
            object_name: 对象名称
            bucket_name: 桶名称

        Returns:
            bool: 对象是否存在
        """
        if bucket_name is None:
            bucket_name = self.config.default_bucket
        try:
            self.client.stat_object(bucket_name, object_name)
            return True
        except S3Error:
            return False

    def get_object_size(
            self,
            object_name: str,
            bucket_name: Optional[str] = None
    ):
        """
        获取对象大小
        Args:
            object_name: 对象名称
            bucket_name: 桶名称

        Returns:
            tuple: (成功标志, 大小或错误信息)
        """
        if bucket_name is None:
            bucket_name = self.config.default_bucket
        try:
            stat_info = self.client.stat_object(bucket_name, object_name)
            return True, stat_info.size
        except S3Error as e:
            print(f"s3 object storage get size [{object_name}] error: {e}")
            return False, "获取对象大小失败"

    def __del__(self):
        pass

if __name__ == '__main__':
    client = MinioClient()
    # 上传
    # print(client.fput_object(
    #     "tool_evaluation/infer_Result/Dataset7.n_RAG_e2e.json",
    #     file_path='data/Dataset7.n_RAG_e2e.json',
    #     content_type="application/json"
    # ))
    # 下载

    status, response = client.download_object(
        "tool_evaluation/infer_Result/Dataset7.n_RAG_e2e.json"
    )
    # 1. 读取内容
    content = response.read()  # 这是bytes

    # 2. 解码为字符串
    content_str = content.decode("utf-8")

    # 3. 解析为 JSON 对象
    data = json.loads(content_str)

    print(data)
