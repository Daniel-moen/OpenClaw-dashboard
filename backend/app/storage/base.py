"""Storage backend protocol."""

from __future__ import annotations

from dataclasses import dataclass
from typing import BinaryIO, Protocol


@dataclass(frozen=True)
class StoredFile:
    sha256: str
    size: int
    path: str  # backend-specific location identifier


class StorageBackend(Protocol):
    def save(self, src: BinaryIO, *, max_bytes: int) -> StoredFile: ...

    def open(self, path: str) -> BinaryIO: ...

    def delete(self, path: str) -> None: ...

    def exists(self, path: str) -> bool: ...
