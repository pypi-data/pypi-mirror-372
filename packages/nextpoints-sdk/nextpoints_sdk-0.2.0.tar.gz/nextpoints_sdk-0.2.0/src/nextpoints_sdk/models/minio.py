# minio.py
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, model_validator


class MinioClientConfig(BaseModel):
    """
    MinIO 专用配置(S3 兼容模式)
    推荐 endpoint_url 使用 http(s)://host:port 形式。
    """

    endpoint_url: str  # 例如 http://minio:9000 或 https://minio.example.com
    access_key_id: str
    secret_access_key: str
    verify_ssl: bool = False  # 自签名证书时可设 False
    presign_enabled: bool = True
    presign_default_expiration: int = 3600  # 秒

    # ✅ 新增：可选默认 bucket 与前缀
    bucket: Optional[str] = None
    bucket_prefix: Optional[str] = None

    # 超时/重试/分片
    connect_timeout_s: float = 5.0
    read_timeout_s: float = 60.0
    max_retries: int = 3
    multipart_threshold_mb: int = 16
    multipart_chunk_mb: int = 8
    max_concurrency: int = 10

    @model_validator(mode="after")
    def _normalize(self):
        if self.bucket_prefix:
            bp = self.bucket_prefix.strip().lstrip("/")
            if bp and not bp.endswith("/"):
                bp += "/"
            self.bucket_prefix = bp
        return self
