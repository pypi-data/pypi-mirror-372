import boto3
import os
from typing import Optional


class S3StorageAdapter:
    """Adapter for AWS S3 storage."""
    def __init__(self, bucket_name: str, aws_access_key_id: Optional[str] = None, aws_secret_access_key: Optional[str] = None, region_name: Optional[str] = None):
        self.bucket_name = bucket_name
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id or os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=aws_secret_access_key or os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=region_name or os.getenv("AWS_REGION")
        )

    def upload_file(self, file_path: str, object_name: Optional[str] = None):
        object_name = object_name or os.path.basename(file_path)
        self.s3.upload_file(file_path, self.bucket_name, object_name)
        print(f"Uploaded {file_path} to s3://{self.bucket_name}/{object_name}")

    def download_file(self, object_name: str, file_path: Optional[str] = None):
        file_path = file_path or object_name
        self.s3.download_file(self.bucket_name, object_name, file_path)
        print(f"Downloaded s3://{self.bucket_name}/{object_name} to {file_path}")
