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
        module = import_module(f".{module_name}", package=__name__)
        __all__.append(module_name)
        # Ensure proper CamelCase class name generation
        base_name = module_name.split("_adapter")[0]
        class_name = "".join(part.capitalize() for part in base_name.split("_")) + "Adapter"
        globals()[module_name] = getattr(module, class_name)
    except ImportError:
        # Dependency not installed, skip adapter
        globals()[module_name] = None
    except Exception:
        # Any other error during import, skip adapter
        globals()[module_name] = None
