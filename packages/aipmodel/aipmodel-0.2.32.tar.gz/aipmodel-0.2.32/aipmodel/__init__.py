from .CephS3Manager import CephS3Manager
from .model_registry import MLOpsManager
from .test import create_model, download_model, get_model, list_models
from .update_checker import check_latest_version

check_latest_version("aipmodel")

__all__ = ["MLOpsManager", "create_model", "download_model", "get_model", "list_models"]

__version__ = "0.2.32"
__description__ = "SDK for model registration, versioning, and storage"
