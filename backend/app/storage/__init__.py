"""Pluggable storage backend (local filesystem by default)."""

from .base import StorageBackend, StoredFile
from .local import LocalStorage

__all__ = ["StorageBackend", "StoredFile", "LocalStorage", "get_storage"]


def get_storage() -> StorageBackend:
    """Return the configured storage backend.

    Add new backends (S3, GCS, etc) by importing them here and selecting via
    an env variable.
    """
    from ..config import get_settings

    settings = get_settings()
    return LocalStorage(settings.uploads_path)
