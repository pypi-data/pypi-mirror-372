# Storage adapters package initialization
# This file ensures Python treats the 'storage' directory as a package.

from importlib import import_module

__all__ = []

# Attempt to import optional storage adapters
optional_adapters = {
    "s3_storage_adapter": "boto3",
    "gcs_storage_adapter": "google.cloud.storage",
    "azure_blob_storage_adapter": "azure.storage.blob",
}

for module_name, dependency in optional_adapters.items():
    try:
        import_module(dependency)
        import_module(f".{module_name}", package=__name__)
        __all__.append(module_name)
        globals()[module_name] = getattr(import_module(f".{module_name}", package=__name__), module_name.split("_adapter")[0].capitalize() + "Adapter")
    except ImportError:
        # Dependency not installed, skip adapter
        globals()[module_name] = None
        pass
