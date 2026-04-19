"""Dashboard summary aggregator."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends

from ..businesses import list_providers
from ..db import get_connection
from ..deps import require_session
from ..models import (
    ActivityItem,
    AssistantAction,
    BusinessSummary,
    DashboardSummary,
    Event,
    Metric,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"], dependencies=[Depends(require_session)])


@router.get("/summary", response_model=DashboardSummary)
async def summary() -> DashboardSummary:
    conn = get_connection()

    vault_row = conn.execute(
        "SELECT COUNT(*) AS c, COALESCE(SUM(size), 0) AS s FROM vault_files"
    ).fetchone()

    now = datetime.now(timezone.utc)
    week_end = now + timedelta(days=7)
    upcoming_rows = conn.execute(
        "SELECT * FROM events WHERE starts_at >= ? AND starts_at <= ? "
        "ORDER BY starts_at ASC LIMIT 5",
        (now.isoformat(), week_end.isoformat()),
    ).fetchall()

    activity_rows = conn.execute(
        "SELECT a.*, p.name AS profile_name "
        "FROM activity a LEFT JOIN profiles p ON p.key = a.profile_key "
        "ORDER BY a.created_at DESC LIMIT 12"
    ).fetchall()

    action_rows = conn.execute(
        "SELECT * FROM assistant_actions ORDER BY category, label LIMIT 8"
    ).fetchall()

    businesses: list[BusinessSummary] = [await p.summary() for p in list_providers()]

    stats = [
        Metric(key="vault_files", label="Vault files", value=vault_row["c"]),
        Metric(
            key="vault_size",
            label="Vault size",
            value=round(vault_row["s"] / (1024 * 1024), 2),
            unit="MB",
        ),
        Metric(
            key="upcoming_events",
            label="Events next 7d",
            value=len(upcoming_rows),
        ),
        Metric(
            key="businesses_live",
            label="Brands live",
            value=sum(1 for b in businesses if b.status == "live"),
        ),
    ]

    return DashboardSummary(
        stats=stats,
        recent_activity=[
            ActivityItem(
                id=r["id"],
                kind=r["kind"],
                message=r["message"],
                meta=json.loads(r["meta_json"]) if r["meta_json"] else None,
                profile_key=r["profile_key"],
                profile_name=r["profile_name"],
                created_at=datetime.fromisoformat(r["created_at"]),
            )
            for r in activity_rows
        ],
        quick_actions=[
            AssistantAction(
                id=r["id"],
                slug=r["slug"],
                label=r["label"],
                prompt=r["prompt"],
                category=r["category"],
                created_at=datetime.fromisoformat(r["created_at"]),
            )
            for r in action_rows
        ],
        businesses=businesses,
        upcoming_events=[
            Event(
                id=r["id"],
                title=r["title"],
                starts_at=datetime.fromisoformat(r["starts_at"]),
                ends_at=datetime.fromisoformat(r["ends_at"]) if r["ends_at"] else None,
                location=r["location"],
                notes=r["notes"],
                created_at=datetime.fromisoformat(r["created_at"]),
            )
            for r in upcoming_rows
        ],
    )
