import os
import logging
import importlib

if importlib.util.find_spec("boto3") is None:
    boto3 = None
else:
    import boto3
try:
    from botocore.exceptions import NoCredentialsError
except ImportError:
    NoCredentialsError = None

try:
    from google.cloud import storage as gcs_storage
except ImportError:
    gcs_storage = None

try:
    from azure.storage.blob import BlobServiceClient
except ImportError:
    BlobServiceClient = None
from typing import List

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class StorageAdapter:
    """Base class for storage adapters."""
    def upload_file(self, file_path: str, destination: str):
        raise NotImplementedError

    def download_file(self, source: str, destination: str):
        raise NotImplementedError

    def list_files(self, prefix: str) -> List[str]:
        raise NotImplementedError

class LocalStorageAdapter(StorageAdapter):
    """Local filesystem storage adapter."""
    def upload_file(self, file_path: str, destination: str):
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        with open(file_path, 'rb') as src, open(destination, 'wb') as dst:
            dst.write(src.read())
        logging.info(f"Uploaded {file_path} to {destination}")

    def download_file(self, source: str, destination: str):
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        with open(source, 'rb') as src, open(destination, 'wb') as dst:
            dst.write(src.read())
        logging.info(f"Downloaded {source} to {destination}")

    def list_files(self, prefix: str) -> List[str]:
        return [os.path.join(dp, f) for dp, dn, filenames in os.walk(prefix) for f in filenames]

class S3StorageAdapter(StorageAdapter):
    """AWS S3 storage adapter."""
    def __init__(self, bucket_name: str, aws_access_key_id: str = None, aws_secret_access_key: str = None, region_name: str = None):
        self.bucket_name = bucket_name
        self.s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)

    def upload_file(self, file_path: str, destination: str):
        try:
            self.s3.upload_file(file_path, self.bucket_name, destination)
            logging.info(f"Uploaded {file_path} to s3://{self.bucket_name}/{destination}")
        except NoCredentialsError:
            logging.error("AWS credentials not found.")

    def download_file(self, source: str, destination: str):
        try:
            self.s3.download_file(self.bucket_name, source, destination)
            logging.info(f"Downloaded s3://{self.bucket_name}/{source} to {destination}")
        except NoCredentialsError:
            logging.error("AWS credentials not found.")

    def list_files(self, prefix: str) -> List[str]:
        response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
        return [item['Key'] for item in response.get('Contents', [])]

class GCSStorageAdapter(StorageAdapter):
    """Google Cloud Storage adapter."""
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.client = gcs_storage.Client()
        self.bucket = self.client.bucket(bucket_name)

    def upload_file(self, file_path: str, destination: str):
        blob = self.bucket.blob(destination)
        blob.upload_from_filename(file_path)
        logging.info(f"Uploaded {file_path} to gs://{self.bucket_name}/{destination}")

    def download_file(self, source: str, destination: str):
        blob = self.bucket.blob(source)
        blob.download_to_filename(destination)
        logging.info(f"Downloaded gs://{self.bucket_name}/{source} to {destination}")

    def list_files(self, prefix: str) -> List[str]:
        return [blob.name for blob in self.client.list_blobs(self.bucket_name, prefix=prefix)]

class AzureBlobStorageAdapter(StorageAdapter):
    """Azure Blob Storage adapter."""
    def __init__(self, connection_string: str, container_name: str):
        self.container_name = container_name
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_client = self.blob_service_client.get_container_client(container_name)

    def upload_file(self, file_path: str, destination: str):
        blob_client = self.container_client.get_blob_client(destination)
        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
        logging.info(f"Uploaded {file_path} to azure://{self.container_name}/{destination}")

    def download_file(self, source: str, destination: str):
        blob_client = self.container_client.get_blob_client(source)
        with open(destination, "wb") as file:
            data = blob_client.download_blob()
            file.write(data.readall())
        logging.info(f"Downloaded azure://{self.container_name}/{source} to {destination}")

    def list_files(self, prefix: str) -> List[str]:
        return [blob.name for blob in self.container_client.list_blobs(name_starts_with=prefix)]
