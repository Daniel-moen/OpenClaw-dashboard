"""Calendar events CRUD."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..db import get_connection, log_activity
from ..deps import current_profile_key, require_session
from ..models import Event, EventIn

router = APIRouter(
    prefix="/calendar", tags=["calendar"], dependencies=[Depends(require_session)]
)


def _row_to_event(row) -> Event:
    return Event(
        id=row["id"],
        title=row["title"],
        starts_at=datetime.fromisoformat(row["starts_at"]),
        ends_at=datetime.fromisoformat(row["ends_at"]) if row["ends_at"] else None,
        location=row["location"],
        notes=row["notes"],
        created_at=datetime.fromisoformat(row["created_at"]),
    )


@router.get("/events", response_model=list[Event])
def list_events(
    start: datetime | None = Query(default=None),
    end: datetime | None = Query(default=None),
) -> list[Event]:
    conn = get_connection()
    if start and end:
        rows = conn.execute(
            "SELECT * FROM events WHERE starts_at >= ? AND starts_at <= ? "
            "ORDER BY starts_at ASC",
            (start.isoformat(), end.isoformat()),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM events ORDER BY starts_at ASC"
        ).fetchall()
    return [_row_to_event(r) for r in rows]


@router.post("/events", response_model=Event, status_code=status.HTTP_201_CREATED)
def create_event(body: EventIn, profile_key: str | None = Depends(current_profile_key)) -> Event:
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO events (title, starts_at, ends_at, location, notes) "
        "VALUES (?, ?, ?, ?, ?)",
        (
            body.title,
            body.starts_at.isoformat(),
            body.ends_at.isoformat() if body.ends_at else None,
            body.location,
            body.notes,
        ),
    )
    row = conn.execute(
        "SELECT * FROM events WHERE id = ?", (cur.lastrowid,)
    ).fetchone()
    log_activity(
        "calendar.create", f"Added event: {body.title}", profile_key=profile_key
    )
    return _row_to_event(row)


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int, profile_key: str | None = Depends(current_profile_key)
) -> None:
    conn = get_connection()
    row = conn.execute("SELECT title FROM events WHERE id = ?", (event_id,)).fetchone()
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "not found")
    conn.execute("DELETE FROM events WHERE id = ?", (event_id,))
    log_activity(
        "calendar.delete", f"Removed event: {row['title']}", profile_key=profile_key
    )
