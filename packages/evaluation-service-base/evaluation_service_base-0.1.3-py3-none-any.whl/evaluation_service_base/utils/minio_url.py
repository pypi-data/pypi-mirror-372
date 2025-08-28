from typing import Optional, Union
from urllib.parse import urlparse, unquote
from dataclasses import dataclass, field
import re


@dataclass
class MinioURL:
    """MinIO URL解析类，用于解析s3://accessKey:secretKey@host:port/bucket-name/path格式的URL"""

    scheme: Optional[str] = field(
        default=None,
        metadata={
            "title": "Scheme",
            "description": "URL协议，通常为s3",
        }
    )

    access_key: Optional[str] = field(
        default=None,
        metadata={
            "title": "Access Key",
            "description": "MinIO访问密钥",
        }
    )

    secret_key: Optional[str] = field(
        default=None,
        metadata={
            "title": "Secret Key",
            "description": "MinIO秘密密钥",
        }
    )

    host: Optional[str] = field(
        default=None,
        metadata={
            "title": "Host",
            "description": "MinIO服务器地址",
        }
    )

    port: Optional[int] = field(
        default=None,
        metadata={
            "title": "Port",
            "description": "MinIO服务器端口",
        }
    )

    bucket_name: Optional[str] = field(
        default=None,
        metadata={
            "title": "Bucket Name",
            "description": "存储桶名称",
        }
    )

    object_path: Optional[str] = field(
        default=None,
        metadata={
            "title": "Object Path",
            "description": "对象文件路径",
        }
    )

    secure: Optional[bool] = field(
        default=False,
        metadata={
            "title": "Secure Connection",
            "description": "是否使用HTTPS连接",
        }
    )

    @classmethod
    def parse_url(cls, url: str) -> 'MinioURL':
        """
        解析MinIO URL

        支持的格式:
        - s3://accessKey:secretKey@localhost:9000/bucket-name/path/to/file
        - s3://accessKey:secretKey@localhost:9000/bucket-name/
        - s3://accessKey:secretKey@localhost:9000/bucket-name

        Args:
            url: MinIO URL字符串

        Returns:
            MinioURL对象

        Raises:
            ValueError: 当URL格式不正确时
        """
        if not url:
            raise ValueError("URL不能为空")

        # 使用正则表达式解析URL
        pattern = r'^(?P<scheme>s3)://(?P<access_key>[^:]+):(?P<secret_key>[^@]+)@(?P<host>[^:]+):(?P<port>\d+)/(?P<bucket>[^/]+)(?P<path>/.*)?$'
        match = re.match(pattern, url)

        if not match:
            raise ValueError(f"无效的MinIO URL格式: {url}")

        groups = match.groupdict()

        # 处理路径
        object_path = groups.get('path', '')
        if object_path and object_path.startswith('/'):
            object_path = object_path[1:]  # 移除开头的斜杠

        # 判断是否使用安全连接
        secure = groups['scheme'] == 'https' or groups['port'] == '443'

        return cls(
            scheme=groups['scheme'],
            access_key=unquote(groups['access_key']),  # URL解码
            secret_key=unquote(groups['secret_key']),  # URL解码
            host=groups['host'],
            port=int(groups['port']),
            bucket_name=groups['bucket'],
            object_path=object_path if object_path else None,
            secure=secure
        )

    def to_minio_config(self) -> dict:
        """
        转换为MinioConfig字典

        Returns:
            包含MinIO配置信息的字典
        """
        if not all([self.access_key, self.secret_key, self.host, self.port]):
            raise ValueError("缺少必要的连接信息")

        return {
            'endpoint': f"{self.host}:{self.port}",
            'access_key': self.access_key,
            'secret_key': self.secret_key,
            'secure': self.secure,
            'cert_check': False,
            'default_bucket': self.bucket_name or 'default',
        }

    def get_endpoint(self) -> str:
        """获取MinIO端点地址"""
        if not self.host or not self.port:
            raise ValueError("缺少主机或端口信息")
        return f"{self.host}:{self.port}"

    def get_full_object_path(self) -> str:
        """获取完整的对象路径（包含桶名）"""
        if not self.bucket_name:
            raise ValueError("缺少桶名称")

        if self.object_path:
            return f"{self.bucket_name}/{self.object_path}"
        return self.bucket_name

    def build_url(self) -> str:
        """
        重构MinIO URL

        Returns:
            完整的MinIO URL字符串
        """
        if not all([self.scheme, self.access_key, self.secret_key, self.host, self.port, self.bucket_name]):
            raise ValueError("缺少构建URL的必要信息")

        base_url = f"{self.scheme}://{self.access_key}:{self.secret_key}@{self.host}:{self.port}/{self.bucket_name}"

        if self.object_path:
            base_url += f"/{self.object_path}"

        return base_url

    def is_valid(self) -> bool:
        """检查URL是否包含所有必要信息"""
        return all([
            self.scheme,
            self.access_key,
            self.secret_key,
            self.host,
            self.port,
            self.bucket_name
        ])

    def __str__(self) -> str:
        """字符串表示"""
        try:
            return self.build_url()
        except ValueError:
            return f"MinioURL(incomplete: scheme={self.scheme}, host={self.host}, bucket={self.bucket_name})"


# 使用示例和测试
if __name__ == "__main__":
    # 测试URL解析
    test_urls = [
        "s3://mykey:mysecret@localhost:9000/my-bucket/data/test.json",
    ]

    for url in test_urls:
        print(f"\n解析URL: {url}")
        try:
            minio_url = MinioURL.parse_url(url)
            print(f"  解析结果: {minio_url}")
            print(f"  MinIO配置: {minio_url.to_minio_config()}")
            print(f"  端点地址: {minio_url.get_endpoint()}")
            print(f"  完整路径: {minio_url.get_full_object_path()}")
            print(f"  URL有效: {minio_url.is_valid()}")
            print(f"  重构URL: {minio_url.build_url()}")
        except Exception as e:
            print(f"  错误: {e}")