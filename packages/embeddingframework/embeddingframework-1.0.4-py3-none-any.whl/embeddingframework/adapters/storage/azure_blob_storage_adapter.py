from azure.storage.blob import BlobServiceClient
import os
from typing import Optional


class AzureBlobStorageAdapter:
    """Adapter for Azure Blob Storage."""
    def __init__(self, container_name: str, connection_string: Optional[str] = None):
        self.container_name = container_name
        self.connection_string = connection_string or os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        if not self.connection_string:
            raise ValueError("Azure Storage connection string must be provided via parameter or AZURE_STORAGE_CONNECTION_STRING environment variable.")
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        self.container_client = self.blob_service_client.get_container_client(container_name)

    def upload_file(self, file_path: str, blob_name: Optional[str] = None):
        blob_name = blob_name or os.path.basename(file_path)
        with open(file_path, "rb") as data:
            self.container_client.upload_blob(name=blob_name, data=data, overwrite=True)
        print(f"Uploaded {file_path} to azure://{self.container_name}/{blob_name}")

    def download_file(self, blob_name: str, file_path: Optional[str] = None):
        file_path = file_path or blob_name
        with open(file_path, "wb") as file:
            data = self.container_client.download_blob(blob_name)
            file.write(data.readall())
        print(f"Downloaded azure://{self.container_name}/{blob_name} to {file_path}")
