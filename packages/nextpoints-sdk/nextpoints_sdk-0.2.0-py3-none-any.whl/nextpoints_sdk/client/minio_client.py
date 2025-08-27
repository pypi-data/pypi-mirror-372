# service.py
from __future__ import annotations
from typing import Optional, Iterable, BinaryIO, Literal, Tuple, Dict, Any, List
from urllib.parse import urlparse
from dataclasses import dataclass
import os, re, json, mimetypes, logging

import os
import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import (
    ClientError,
    EndpointConnectionError,
    ConnectionClosedError,
)
from boto3.s3.transfer import TransferConfig

# 可选：图像读取（若不需要可删）
import numpy as np
import cv2  # pip install opencv-python-headless

from ..models.minio import MinioClientConfig

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class _EndpointParts:
    scheme: str
    netloc: str
    base_path: str  # 一般为空；如使用了反向代理 path 前缀可出现


CONTENT_TYPE_MAP = {
    ".pcd": "application/octet-stream",
    ".bin": "application/octet-stream",
    ".ply": "application/octet-stream",
    ".json": "application/json",
    ".txt": "text/plain; charset=utf-8",
    ".csv": "text/csv; charset=utf-8",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".gif": "image/gif",
    ".bmp": "image/bmp",
    ".mp4": "video/mp4",
    ".mov": "video/quicktime",
}


def _guess_content_type(filename_or_key: str) -> str:
    name = filename_or_key.lower()
    for ext, ct in CONTENT_TYPE_MAP.items():
        if name.endswith(ext):
            return ct
    guessed, _ = mimetypes.guess_type(filename_or_key)
    return guessed or "application/octet-stream"


# ---- 统一的简单异常 ----
class StorageError(Exception): ...


class AuthError(StorageError): ...


class PermissionDenied(StorageError): ...


class NotFound(StorageError): ...


class EndpointError(StorageError): ...


class UnsupportedOperation(StorageError): ...


class MinioClient:
    """
    MinIO 客户端封装(不写死 bucket;支持配置默认 bucket/bucket_prefix)
    规则：
      - 每个方法的 bucket_name 形参（若提供）优先级最高；
      - 未提供时，回退到 config.bucket;
      - 对象 key 自动应用 config.bucket_prefix(若存在)
    Path-Style URL:{endpoint}/{bucket}/{key_with_prefix}
    """

    # 显式声明，避免类型检查器报未知属性
    _ep: _EndpointParts

    def __init__(self, cfg: MinioClientConfig):
        self.cfg = cfg

        s3cfg = BotoConfig(
            s3={"addressing_style": "path"},
            retries={"max_attempts": cfg.max_retries, "mode": "standard"},
            connect_timeout=cfg.connect_timeout_s,
            read_timeout=cfg.read_timeout_s,
        )
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=cfg.access_key_id,
            aws_secret_access_key=cfg.secret_access_key,
            endpoint_url=cfg.endpoint_url,
            verify=cfg.verify_ssl,
            config=s3cfg,
        )

        parsed = urlparse(cfg.endpoint_url)
        self._ep = _EndpointParts(parsed.scheme, parsed.netloc, parsed.path.rstrip("/"))

        self._transfer_cfg = TransferConfig(
            multipart_threshold=cfg.multipart_threshold_mb * 1024 * 1024,
            multipart_chunksize=cfg.multipart_chunk_mb * 1024 * 1024,
            max_concurrency=cfg.max_concurrency,
            use_threads=True,
        )

    # --------- 内部工具 ---------

    def _resolve_bucket(self, bucket_name: Optional[str]) -> str:
        """
        传参优先，否则用配置默认；都没有则抛错。
        """
        bucket = (bucket_name or self.cfg.bucket or "").strip()
        if not bucket:
            raise ValueError(
                "bucket_name is required (no default 'bucket' in MinioClientConfig)."
            )
        return bucket

    def _apply_prefix(self, key: str) -> str:
        """
        将 config.bucket_prefix 应用于对象键（若存在）。
        传入的 key 视为“相对路径”，自动 lstrip('/') 以避免双斜杠。
        """
        key = key.lstrip("/")
        if self.cfg.bucket_prefix:
            return f"{self.cfg.bucket_prefix}{key}"
        return key

    def _build_direct_url(self, bucket: str, key: str) -> str:
        """
        Path-Style 直链：
        {scheme}://{netloc}/{base_path}{/}{bucket}/{key_with_prefix}
        """
        parts = self._ep
        base_path = (parts.base_path + "/") if parts.base_path else ""
        return f"{parts.scheme}://{parts.netloc}/{base_path}{bucket}/{self._apply_prefix(key)}"

    @staticmethod
    def _map_client_error(e: ClientError) -> StorageError:
        code = str(e.response.get("Error", {}).get("Code", ""))
        status = int(e.response.get("ResponseMetadata", {}).get("HTTPStatusCode", 0))
        if status in (404, 301) or code in (
            "NoSuchBucket",
            "NoSuchKey",
            "NotFound",
            "404",
        ):
            return NotFound(str(e))
        if status == 403 or code in ("AccessDenied", "403"):
            return PermissionDenied(str(e))
        if status == 401 or code in ("InvalidAccessKeyId", "SignatureDoesNotMatch"):
            return AuthError(str(e))
        return StorageError(str(e))

    # --------- 对外 API（传参优先，否则用默认） ---------

    def test_connection(self, bucket_name: Optional[str] = None) -> Tuple[bool, str]:
        bucket = self._resolve_bucket(bucket_name)
        try:
            self.s3.head_bucket(Bucket=bucket)
            # 若配置了前缀，做一次轻量列举校验
            if self.cfg.bucket_prefix:
                self.s3.list_objects_v2(
                    Bucket=bucket, Prefix=self.cfg.bucket_prefix, MaxKeys=1
                )
            return True, "Connection successful"
        except EndpointConnectionError as e:
            return False, f"Endpoint unreachable: {e}"
        except ClientError as e:
            mapped = self._map_client_error(e)
            return False, f"{mapped.__class__.__name__}: {mapped}"
        except Exception as e:
            return False, f"Error: {e}"

    def object_exists(
        self, bucket_name: Optional[str], key: str, *, version_id: Optional[str] = None
    ) -> bool:
        bucket = self._resolve_bucket(bucket_name)
        try:
            kwargs: Dict[str, Any] = {"Bucket": bucket, "Key": self._apply_prefix(key)}
            if version_id:
                kwargs["VersionId"] = version_id
            self.s3.head_object(**kwargs)
            return True
        except ClientError as e:
            mapped = self._map_client_error(e)
            if isinstance(mapped, NotFound):
                return False
            raise mapped

    def list_objects(self, bucket_name: Optional[str], prefix: str = "") -> List[str]:
        bucket = self._resolve_bucket(bucket_name)
        abs_prefix = self._apply_prefix(prefix)
        keys: List[str] = []
        paginator = self.s3.get_paginator("list_objects_v2")
        try:
            for page in paginator.paginate(Bucket=bucket, Prefix=abs_prefix):
                for obj in page.get("Contents", []):
                    # 返回应用了前缀的“绝对键”；如需相对可在外部切割 cfg.bucket_prefix
                    keys.append(obj["Key"])
            logger.info(
                f"Found {len(keys)} objects under '{abs_prefix}' in bucket '{bucket}'."
            )
            return keys
        except ClientError as e:
            logger.error(f"List objects failed: {e}")
            return keys

    def list_all_objects(self, bucket_name: Optional[str], prefix: str) -> List[Dict]:
        bucket = self._resolve_bucket(bucket_name)
        abs_prefix = self._apply_prefix(prefix)
        paginator = self.s3.get_paginator("list_objects_v2")
        all_objects: List[Dict] = []
        for page in paginator.paginate(Bucket=bucket, Prefix=abs_prefix):
            if "Contents" in page:
                all_objects.extend(page["Contents"])
        return all_objects

    def read_json_object(self, bucket_name: Optional[str], key: str):
        bucket = self._resolve_bucket(bucket_name)
        try:
            resp = self.s3.get_object(Bucket=bucket, Key=self._apply_prefix(key))
            return json.loads(resp["Body"].read().decode("utf-8"))
        except Exception as e:
            logger.error(f"Error reading JSON s3://{bucket}/{key}: {e}")
            raise

    def upload_json_object(
        self, bucket_name: Optional[str], key: str, data: Any
    ) -> None:
        bucket = self._resolve_bucket(bucket_name)
        try:
            self.s3.put_object(
                Bucket=bucket,
                Key=self._apply_prefix(key),
                Body=json.dumps(data, indent=2, ensure_ascii=False),
                ContentType="application/json",
            )
        except ClientError as e:
            logger.error(f"Error uploading JSON to s3://{bucket}/{key}: {e}")
            raise

    def get_object(
        self,
        bucket_name: Optional[str],
        object_key: str,
        *,
        stream: bool = False,
        range: Optional[Tuple[int, int]] = None,
    ):
        bucket = self._resolve_bucket(bucket_name)
        kwargs: Dict[str, Any] = {
            "Bucket": bucket,
            "Key": self._apply_prefix(object_key),
        }
        if range:
            kwargs["Range"] = f"bytes={range[0]}-{range[1]}"
        try:
            resp = self.s3.get_object(**kwargs)
            body = resp["Body"]
            return body if stream else body.read()
        except ClientError as e:
            raise self._map_client_error(e)
        except (EndpointConnectionError, ConnectionClosedError) as e:
            raise EndpointError(str(e))

    def put_object(
        self,
        bucket_name: Optional[str],
        object_key: str,
        data: bytes | BinaryIO,
        *,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> bool:
        bucket = self._resolve_bucket(bucket_name)
        extra: Dict[str, Any] = {}
        if content_type:
            extra["ContentType"] = content_type
        if metadata:
            extra["Metadata"] = metadata
        try:
            self.s3.put_object(
                Bucket=bucket, Key=self._apply_prefix(object_key), Body=data, **extra
            )
            return True
        except ClientError as e:
            logger.error(f"Put object failed: {e}")
            return False

    def copy_object(
        self,
        source_bucket: Optional[str],
        source_key: str,
        dest_bucket: Optional[str],
        dest_key: str,
    ) -> bool:
        src_bucket = self._resolve_bucket(source_bucket)
        dst_bucket = self._resolve_bucket(dest_bucket)
        try:
            _, ext = os.path.splitext(dest_key)
            content_type = CONTENT_TYPE_MAP.get(ext.lower()) or _guess_content_type(
                dest_key
            )
            self.s3.copy_object(
                CopySource={
                    "Bucket": src_bucket,
                    "Key": self._apply_prefix(source_key),
                },
                Bucket=dst_bucket,
                Key=self._apply_prefix(dest_key),
                ContentType=content_type,
                ContentDisposition="inline",
                MetadataDirective="REPLACE",
            )
            return True
        except ClientError as e:
            logger.error(f"Copy object failed: {e}")
            return False

    def delete_object(
        self,
        bucket_name: Optional[str],
        object_key: str,
        *,
        version_id: Optional[str] = None,
    ) -> None:
        bucket = self._resolve_bucket(bucket_name)
        kwargs = {"Bucket": bucket, "Key": self._apply_prefix(object_key)}
        if version_id:
            kwargs["VersionId"] = version_id
        try:
            self.s3.delete_object(**kwargs)
        except ClientError as e:
            raise self._map_client_error(e)

    def generate_presigned_url(
        self,
        bucket_name: Optional[str],
        object_key: str,
        expiration: Optional[int] = None,
        *,
        op: Literal["get", "put"] = "get",
    ) -> str:
        if not self.cfg.presign_enabled:
            raise UnsupportedOperation("Presign is disabled by configuration.")
        bucket = self._resolve_bucket(bucket_name)
        ttl = int(expiration or self.cfg.presign_default_expiration)
        try:
            if op == "get":
                return self.s3.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": bucket, "Key": self._apply_prefix(object_key)},
                    ExpiresIn=ttl,
                )
            elif op == "put":
                return self.s3.generate_presigned_url(
                    "put_object",
                    Params={"Bucket": bucket, "Key": self._apply_prefix(object_key)},
                    ExpiresIn=ttl,
                )
            else:
                raise UnsupportedOperation(f"Unsupported presign op: {op}")
        except ClientError as e:
            raise self._map_client_error(e)

    def get_object_url(
        self,
        bucket_name: Optional[str],
        object_key: str,
        use_presigned: bool = False,
        expiration: Optional[int] = None,
    ) -> str:
        bucket = self._resolve_bucket(bucket_name)
        if use_presigned:
            return self.generate_presigned_url(bucket, object_key, expiration, op="get")
        return self._build_direct_url(bucket, object_key)

    # -------- 可选：图像读取（与原接口对齐） --------

    def read_image_object(
        self,
        bucket_name: Optional[str],
        key: str,
        color: Literal["rgb", "bgr", "gray", "unchanged"] = "rgb",
    ) -> np.ndarray:
        bucket = self._resolve_bucket(bucket_name)
        try:
            resp = self.s3.get_object(Bucket=bucket, Key=self._apply_prefix(key))
            data = resp["Body"].read()
        except Exception as e:
            logger.error(f"Error reading image object s3://{bucket}/{key}: {e}")
            raise

        nparr = np.frombuffer(data, np.uint8)
        flag_map = {
            "bgr": cv2.IMREAD_COLOR,
            "rgb": cv2.IMREAD_COLOR,
            "gray": cv2.IMREAD_GRAYSCALE,
            "unchanged": cv2.IMREAD_UNCHANGED,
        }
        img = cv2.imdecode(nparr, flag_map[color])
        if img is None:
            raise ValueError(f"cv2.imdecode failed for s3://{bucket}/{key}")
        if color == "rgb" and img.ndim == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img

    # -------- 文件/文件夹上传（显式或默认 bucket 均可） --------

    def upload_file(
        self,
        local_path: str,
        bucket_name: Optional[str],
        object_key: str,
        *,
        content_type: Optional[str] = None,
        inline: bool = True,
    ) -> bool:
        bucket = self._resolve_bucket(bucket_name)
        if not os.path.isfile(local_path):
            logger.error(f"Local file not found: {local_path}")
            return False
        if not content_type:
            content_type = _guess_content_type(object_key or local_path)
        extra_args: Dict[str, Any] = {"ContentType": content_type}
        if inline:
            extra_args["ContentDisposition"] = "inline"
        try:
            self.s3.upload_file(
                Filename=local_path,
                Bucket=bucket,
                Key=self._apply_prefix(object_key),
                ExtraArgs=extra_args,
                Config=self._transfer_cfg,
            )
            return True
        except ClientError as e:
            logger.error(f"Upload file failed: {e}")
            return False

    def upload_folder(
        self,
        local_folder_path: str,
        bucket_name: Optional[str],
        object_prefix: str = "",
        *,
        include_folder_name: bool = True,
    ) -> int:
        bucket = self._resolve_bucket(bucket_name)
        local_folder_path = os.path.normpath(local_folder_path)
        if not os.path.isdir(local_folder_path):
            logger.error(f"Local folder not found: {local_folder_path}")
            return 0

        # 规范前缀（再交给 _apply_prefix 二次前缀拼接）
        object_prefix = object_prefix.strip().lstrip("/")
        if object_prefix and not object_prefix.endswith("/"):
            object_prefix += "/"
        if include_folder_name:
            object_prefix += os.path.basename(local_folder_path) + "/"

        uploaded = 0
        for root, _, files in os.walk(local_folder_path):
            for fname in files:
                src = os.path.join(root, fname)
                rel = os.path.relpath(src, local_folder_path).replace(os.sep, "/")
                key = f"{object_prefix}{rel}"
                if self.upload_file(src, bucket, key):
                    uploaded += 1
        logger.info(f"Folder uploaded. success={uploaded}")
        return uploaded

    # -------- （可选）帧聚合示例，保留你原工具逻辑 --------

    def sync_project_data(
        self, bucket_name: Optional[str], bucket_prefix: str = ""
    ) -> List[Dict]:
        bucket = self._resolve_bucket(bucket_name)
        try:
            objects = self.list_objects(bucket, bucket_prefix)
            frames_data: List[Dict] = []
            pointcloud_files: Dict[str, str] = {}
            image_files: Dict[str, Dict[str, str]] = {}
            pose_files: Dict[str, str] = {}
            timestamp_pattern = r"(\d{10,})"

            for key in objects:
                ts_match = re.search(timestamp_pattern, os.path.basename(key))
                if not ts_match:
                    continue
                ts = ts_match.group(1)
                if key.endswith((".pcd", ".bin", ".ply")):
                    pointcloud_files[ts] = key
                elif key.endswith((".jpg", ".jpeg", ".png")):
                    cam_id = self._extract_camera_id(key)
                    image_files.setdefault(ts, {})[cam_id] = key
                elif key.endswith(".json") and "pose" in key.lower():
                    pose_files[ts] = key

            for ts, pcd_key in pointcloud_files.items():
                frames_data.append(
                    {
                        "timestamp_ns": ts,
                        "pointcloud_s3_key": pcd_key,
                        "images": image_files.get(ts, {}),
                        "pose_s3_key": pose_files.get(ts),
                    }
                )

            frames_data.sort(key=lambda x: x["timestamp_ns"])
            logger.info(
                f"Synced {len(frames_data)} frames from s3://{bucket}/{bucket_prefix}"
            )
            return frames_data
        except Exception as e:
            logger.error(f"Failed to sync project data: {e}")
            raise

    @staticmethod
    def _extract_camera_id(file_path: str) -> str:
        basename = os.path.basename(file_path).lower()
        patterns = [
            r"cam_?(\d+)",
            r"camera_?(\d+)",
            r"front|back|left|right",
            r"(front_left|front_right|back_left|back_right)",
        ]
        for p in patterns:
            m = re.search(p, basename)
            if m:
                return m.group(1) if m.groups() else m.group(0)
        return "default"
