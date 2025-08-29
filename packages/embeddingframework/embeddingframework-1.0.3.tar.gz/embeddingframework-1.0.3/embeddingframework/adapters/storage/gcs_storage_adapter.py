from google.cloud import storage
import os
from typing import Optional


class GCSStorageAdapter:
    """Adapter for Google Cloud Storage."""
    def __init__(self, bucket_name: str, credentials_path: Optional[str] = None):
        if credentials_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        self.bucket_name = bucket_name
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)

    def upload_file(self, file_path: str, object_name: Optional[str] = None):
        object_name = object_name or os.path.basename(file_path)
        blob = self.bucket.blob(object_name)
        blob.upload_from_filename(file_path)
        print(f"Uploaded {file_path} to gs://{self.bucket_name}/{object_name}")

    def download_file(self, object_name: str, file_path: Optional[str] = None):
        file_path = file_path or object_name
        blob = self.bucket.blob(object_name)
        blob.download_to_filename(file_path)
        print(f"Downloaded gs://{self.bucket_name}/{object_name} to {file_path}")
