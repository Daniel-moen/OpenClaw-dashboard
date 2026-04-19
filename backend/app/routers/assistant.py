"""Assistant quick-action prompts (CRUD)."""

from __future__ import annotations

import re
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from ..db import get_connection
from ..deps import require_session
from ..models import AssistantAction, AssistantActionIn

router = APIRouter(
    prefix="/assistant", tags=["assistant"], dependencies=[Depends(require_session)]
)

SLUG_RE = re.compile(r"[^a-z0-9]+")


def _slugify(label: str) -> str:
    base = SLUG_RE.sub("-", label.lower()).strip("-")
    return base or "action"


def _row(row) -> AssistantAction:
    return AssistantAction(
        id=row["id"],
        slug=row["slug"],
        label=row["label"],
        prompt=row["prompt"],
        category=row["category"],
        created_at=datetime.fromisoformat(row["created_at"]),
    )


@router.get("/actions", response_model=list[AssistantAction])
def list_actions() -> list[AssistantAction]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM assistant_actions ORDER BY category, label"
    ).fetchall()
    return [_row(r) for r in rows]


@router.post("/actions", response_model=AssistantAction, status_code=status.HTTP_201_CREATED)
def create_action(body: AssistantActionIn) -> AssistantAction:
    conn = get_connection()
    base_slug = _slugify(body.label)
    slug = base_slug
    n = 1
    while conn.execute(
        "SELECT 1 FROM assistant_actions WHERE slug = ?", (slug,)
    ).fetchone():
        n += 1
        slug = f"{base_slug}-{n}"
    cur = conn.execute(
        "INSERT INTO assistant_actions (slug, label, prompt, category) "
        "VALUES (?, ?, ?, ?)",
        (slug, body.label, body.prompt, body.category),
    )
    row = conn.execute(
        "SELECT * FROM assistant_actions WHERE id = ?", (cur.lastrowid,)
    ).fetchone()
    return _row(row)


@router.put("/actions/{action_id}", response_model=AssistantAction)
def update_action(action_id: int, body: AssistantActionIn) -> AssistantAction:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM assistant_actions WHERE id = ?", (action_id,)
    ).fetchone()
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "not found")
    conn.execute(
        "UPDATE assistant_actions SET label = ?, prompt = ?, category = ? WHERE id = ?",
        (body.label, body.prompt, body.category, action_id),
    )
    row = conn.execute(
        "SELECT * FROM assistant_actions WHERE id = ?", (action_id,)
    ).fetchone()
    return _row(row)


@router.delete("/actions/{action_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_action(action_id: int) -> None:
    conn = get_connection()
    row = conn.execute(
        "SELECT 1 FROM assistant_actions WHERE id = ?", (action_id,)
    ).fetchone()
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "not found")
    conn.execute("DELETE FROM assistant_actions WHERE id = ?", (action_id,))
