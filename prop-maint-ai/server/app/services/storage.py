import os
import uuid
from typing import Tuple

try:
    import boto3  # type: ignore
except Exception:
    boto3 = None  # type: ignore


class StorageBackend:
    def __init__(self) -> None:
        self.backend = os.getenv("STORAGE_BACKEND", "local").lower()  # 'local' or 's3'
        self.local_dir = os.getenv("LOCAL_UPLOAD_DIR", "uploads")
        self.s3_bucket = os.getenv("S3_BUCKET")
        self.s3_prefix = os.getenv("S3_PREFIX", "")
        self.s3_region = os.getenv("AWS_REGION")
        self.s3_endpoint = os.getenv("S3_ENDPOINT_URL")
        if self.backend == "s3" and boto3 is None:
            raise RuntimeError("boto3 not installed for S3 backend")
        if self.backend == "s3":
            session = boto3.session.Session()
            self.s3 = session.client(
                "s3",
                region_name=self.s3_region,
                endpoint_url=self.s3_endpoint,
            )
        else:
            os.makedirs(self.local_dir, exist_ok=True)

    def save_bytes(self, data: bytes, original_filename: str) -> Tuple[str, str]:
        """Save bytes and return (url_or_path, key).
        - local: returns (path, filename)
        - s3: returns (https url, object key)
        """
        ext = os.path.splitext(original_filename)[1]
        key = f"{uuid.uuid4().hex}{ext}"
        if self.backend == "s3":
            assert self.s3_bucket, "S3_BUCKET not set"
            object_key = f"{self.s3_prefix.rstrip('/')}/{key}" if self.s3_prefix else key
            self.s3.put_object(Bucket=self.s3_bucket, Key=object_key, Body=data, ContentType=_guess_mime(ext))
            url = f"https://{self.s3_bucket}.s3.amazonaws.com/{object_key}"
            return url, object_key
        # local
        file_path = os.path.join(self.local_dir, key)
        with open(file_path, "wb") as f:
            f.write(data)
        return file_path, key


def _guess_mime(ext: str) -> str:
    e = (ext or "").lower()
    if e in (".jpg", ".jpeg"): return "image/jpeg"
    if e == ".png": return "image/png"
    if e == ".gif": return "image/gif"
    return "application/octet-stream"