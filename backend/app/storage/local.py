"""Local filesystem implementation of StorageBackend."""

from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path
from typing import BinaryIO

from .base import StoredFile

CHUNK = 1024 * 1024  # 1 MiB


class UploadTooLarge(Exception):
    pass


class LocalStorage:
    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path_for(self, sha256: str) -> Path:
        return self.root / sha256[:2] / sha256[2:4] / sha256

    def save(self, src: BinaryIO, *, max_bytes: int) -> StoredFile:
        hasher = hashlib.sha256()
        size = 0
        # Stream into a temp file inside the storage root so the final move
        # is atomic and on the same filesystem.
        tmp = tempfile.NamedTemporaryFile(
            dir=self.root, delete=False, prefix=".upload-", suffix=".part"
        )
        try:
            while True:
                chunk = src.read(CHUNK)
                if not chunk:
                    break
                size += len(chunk)
                if size > max_bytes:
                    raise UploadTooLarge(f"upload exceeds {max_bytes} bytes")
                hasher.update(chunk)
                tmp.write(chunk)
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp.close()

            digest = hasher.hexdigest()
            dest = self._path_for(digest)
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.exists():
                # Identical content already stored; drop the temp.
                os.unlink(tmp.name)
            else:
                os.replace(tmp.name, dest)
            return StoredFile(sha256=digest, size=size, path=str(dest.relative_to(self.root)))
        except Exception:
            try:
                os.unlink(tmp.name)
            except OSError:
                pass
            raise

    def open(self, path: str) -> BinaryIO:
        return (self.root / path).open("rb")

    def delete(self, path: str) -> None:
        p = self.root / path
        if p.exists():
            try:
                p.unlink()
            except OSError:
                pass

    def exists(self, path: str) -> bool:
        return (self.root / path).exists()
