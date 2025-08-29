import os
import mimetypes
import logging
from typing import List

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def get_file_metadata(file_path: str) -> dict:
    """Retrieve file metadata including name, size, and MIME type."""
    try:
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)
        return {
            "file_name": file_name,
            "file_size": file_size,
            "mime_type": mime_type or "application/octet-stream"
        }
    except Exception as e:
        logging.error(f"Failed to get metadata for {file_path}: {e}")
        return {}

def list_files_in_directory(directory: str, extensions: List[str] = None) -> List[str]:
    """List all files in a directory, optionally filtering by extensions."""
    try:
        files = []
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                if not extensions or any(filename.lower().endswith(ext.lower()) for ext in extensions):
                    files.append(os.path.join(root, filename))
        return files
    except Exception as e:
        logging.error(f"Failed to list files in {directory}: {e}")
        return []
