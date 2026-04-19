"""Storage vault: list / upload / download / delete."""

from __future__ import annotations

import re
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import StreamingResponse

from ..config import Settings, get_settings
from ..db import get_connection, log_activity
from ..deps import current_profile_key, require_session
from ..models import VaultFile
from ..storage import get_storage
from ..storage.local import UploadTooLarge

router = APIRouter(prefix="/vault", tags=["vault"], dependencies=[Depends(require_session)])

ALLOWED_MIME_PREFIXES = (
    "image/",
    "text/",
    "application/pdf",
    "application/json",
    "application/zip",
    "application/x-zip-compressed",
    "application/octet-stream",
    "application/vnd.openxmlformats-officedocument",
    "application/msword",
    "application/vnd.ms-excel",
    "application/vnd.ms-powerpoint",
    "application/vnd.oasis.opendocument",
    "video/",
    "audio/",
)

UNSAFE_NAME = re.compile(r"[^A-Za-z0-9._\- ]+")


def _safe_name(name: str) -> str:
    name = name.strip().replace("/", "_").replace("\\", "_")
    name = UNSAFE_NAME.sub("_", name)
    return (name or "file")[:200]


def _row_to_file(row) -> VaultFile:
    return VaultFile(
        id=row["id"],
        name=row["name"],
        original_name=row["original_name"],
        mime=row["mime"],
        size=row["size"],
        sha256=row["sha256"],
        created_at=datetime.fromisoformat(row["created_at"]),
    )


@router.get("", response_model=list[VaultFile])
def list_files(q: str | None = Query(default=None, max_length=200)) -> list[VaultFile]:
    conn = get_connection()
    if q:
        rows = conn.execute(
            "SELECT * FROM vault_files WHERE name LIKE ? OR original_name LIKE ? "
            "ORDER BY created_at DESC",
            (f"%{q}%", f"%{q}%"),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM vault_files ORDER BY created_at DESC"
        ).fetchall()
    return [_row_to_file(r) for r in rows]


@router.post("", response_model=VaultFile, status_code=status.HTTP_201_CREATED)
async def upload(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
    profile_key: str | None = Depends(current_profile_key),
) -> VaultFile:
    if not file.filename:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "missing filename")
    mime = file.content_type or "application/octet-stream"
    if not any(mime.startswith(p) for p in ALLOWED_MIME_PREFIXES):
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, f"mime not allowed: {mime}"
        )

    storage = get_storage()
    try:
        stored = storage.save(file.file, max_bytes=settings.max_upload_mb * 1024 * 1024)
    except UploadTooLarge as e:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, str(e)) from e

    conn = get_connection()
    safe = _safe_name(file.filename)
    existing = conn.execute(
        "SELECT * FROM vault_files WHERE sha256 = ?", (stored.sha256,)
    ).fetchone()
    if existing:
        log_activity(
            "vault.upload.dedup",
            f"Re-uploaded {safe} (deduped)",
            profile_key=profile_key,
        )
        return _row_to_file(existing)

    cur = conn.execute(
        "INSERT INTO vault_files (name, original_name, mime, size, sha256, path) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (safe, file.filename, mime, stored.size, stored.sha256, stored.path),
    )
    row = conn.execute(
        "SELECT * FROM vault_files WHERE id = ?", (cur.lastrowid,)
    ).fetchone()
    log_activity(
        "vault.upload",
        f"Uploaded {safe}",
        f'{{"size":{stored.size},"mime":"{mime}"}}',
        profile_key=profile_key,
    )
    return _row_to_file(row)


@router.get("/{file_id}/download")
def download(file_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM vault_files WHERE id = ?", (file_id,)).fetchone()
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "not found")
    storage = get_storage()
    if not storage.exists(row["path"]):
        raise HTTPException(status.HTTP_410_GONE, "file missing on disk")
    fh = storage.open(row["path"])
    headers = {
        "Content-Disposition": f'attachment; filename="{row["name"]}"',
        "X-Content-Type-Options": "nosniff",
        "Cache-Control": "private, max-age=0, no-store",
    }
    return StreamingResponse(fh, media_type=row["mime"], headers=headers)


@router.get("/{file_id}/preview")
def preview(file_id: int):
    """Inline view (used by the UI for image/text preview)."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM vault_files WHERE id = ?", (file_id,)).fetchone()
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "not found")
    storage = get_storage()
    if not storage.exists(row["path"]):
        raise HTTPException(status.HTTP_410_GONE, "file missing on disk")
    fh = storage.open(row["path"])
    headers = {
        "Content-Disposition": f'inline; filename="{row["name"]}"',
        "X-Content-Type-Options": "nosniff",
    }
    return StreamingResponse(fh, media_type=row["mime"], headers=headers)


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(file_id: int, profile_key: str | None = Depends(current_profile_key)) -> None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM vault_files WHERE id = ?", (file_id,)).fetchone()
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "not found")
    conn.execute("DELETE FROM vault_files WHERE id = ?", (file_id,))
    storage = get_storage()
    # Only remove the blob if no other rows reference the same hash.
    others = conn.execute(
        "SELECT 1 FROM vault_files WHERE sha256 = ? LIMIT 1", (row["sha256"],)
    ).fetchone()
    if not others:
        storage.delete(row["path"])
    log_activity("vault.delete", f"Deleted {row['name']}", profile_key=profile_key)
