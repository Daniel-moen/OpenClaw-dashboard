"""JobCarver stats provider.

Proxies an external stats API when ``JOBCARVER_STATS_URL`` is configured.
Falls back to a typed mock so the dashboard stays fully usable out of the
box and the assistant can iterate on the UI before the upstream is wired.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from ..config import get_settings
from ..models import BusinessStats, BusinessSummary, Metric, Series, SeriesPoint


class JobCarverProvider:
    slug = "jobcarver"
    name = "JobCarver"
    tagline = "Job board + scraper ops"
    status = "live"

    async def summary(self) -> BusinessSummary:
        stats = await self.stats()
        headline = {m.key: m.value for m in stats.metrics[:4]}
        return BusinessSummary(
            slug=self.slug,
            name=self.name,
            tagline=self.tagline,
            status=self.status,
            headline=headline,
        )

    async def stats(self) -> BusinessStats:
        settings = get_settings()
        if settings.jobcarver_stats_url:
            try:
                payload = await self._fetch_live(
                    settings.jobcarver_stats_url, settings.jobcarver_stats_token
                )
                return self._normalize(payload, source="live")
            except Exception:  # noqa: BLE001 - fall back to mock so UI keeps working
                pass
        return self._normalize(_mock_payload(), source="mock")

    async def _fetch_live(self, url: str, token: str | None) -> dict[str, Any]:
        headers = {"Accept": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(url, headers=headers)
            r.raise_for_status()
            return r.json()

    def _normalize(self, payload: dict[str, Any], *, source: str) -> BusinessStats:
        metrics_raw = payload.get("metrics") or _derive_metrics_from_flat(payload)
        metrics = [Metric(**m) for m in metrics_raw]

        series: list[Series] = []
        for s in payload.get("series", []):
            points = [SeriesPoint(t=str(p.get("t")), v=p.get("v", 0)) for p in s.get("points", [])]
            series.append(Series(key=s["key"], label=s.get("label", s["key"]), points=points))

        tables = payload.get("tables", {}) or {}

        return BusinessStats(
            slug=self.slug,
            name=self.name,
            fetched_at=datetime.now(timezone.utc),
            source=source,
            metrics=metrics,
            series=series,
            tables=tables,
            raw=payload,
        )


def _derive_metrics_from_flat(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """If the upstream returns a flat dict, surface the obvious numbers."""
    out: list[dict[str, Any]] = []
    for k, v in payload.items():
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            out.append({"key": k, "label": k.replace("_", " ").title(), "value": v})
    return out


def _mock_payload() -> dict[str, Any]:
    """A typed, realistic-looking mock payload used until the live URL is set."""
    rng = random.Random(7)
    today = datetime.now(timezone.utc).date()
    days = [today - timedelta(days=i) for i in range(13, -1, -1)]
    jobs_per_day = [rng.randint(120, 380) for _ in days]
    revenue_per_day = [round(rng.uniform(80, 420), 2) for _ in days]

    metrics = [
        {"key": "jobs_total", "label": "Jobs scraped (14d)", "value": sum(jobs_per_day)},
        {"key": "jobs_today", "label": "Jobs today", "value": jobs_per_day[-1]},
        {
            "key": "revenue_today",
            "label": "Revenue today",
            "value": revenue_per_day[-1],
            "unit": "USD",
        },
        {"key": "active_scrapers", "label": "Active scrapers", "value": 7},
        {"key": "errors_24h", "label": "Errors (24h)", "value": rng.randint(0, 8)},
        {"key": "queue_depth", "label": "Queue depth", "value": rng.randint(0, 120)},
        {
            "key": "avg_response_ms",
            "label": "Avg response",
            "value": rng.randint(120, 480),
            "unit": "ms",
        },
        {
            "key": "uptime_30d",
            "label": "Uptime (30d)",
            "value": round(rng.uniform(99.0, 99.99), 2),
            "unit": "%",
        },
    ]

    series = [
        {
            "key": "jobs_per_day",
            "label": "Jobs scraped per day",
            "points": [{"t": d.isoformat(), "v": v} for d, v in zip(days, jobs_per_day)],
        },
        {
            "key": "revenue_per_day",
            "label": "Revenue per day (USD)",
            "points": [{"t": d.isoformat(), "v": v} for d, v in zip(days, revenue_per_day)],
        },
    ]

    tables = {
        "top_sources": [
            {"source": "indeed", "jobs": rng.randint(2000, 5000), "errors": rng.randint(0, 20)},
            {"source": "linkedin", "jobs": rng.randint(1500, 4000), "errors": rng.randint(0, 15)},
            {"source": "ziprecruiter", "jobs": rng.randint(800, 2500), "errors": rng.randint(0, 10)},
            {"source": "glassdoor", "jobs": rng.randint(500, 2000), "errors": rng.randint(0, 8)},
            {"source": "monster", "jobs": rng.randint(200, 1200), "errors": rng.randint(0, 5)},
        ],
        "recent_runs": [
            {
                "scraper": f"scraper-{i}",
                "started_at": (datetime.now(timezone.utc) - timedelta(minutes=i * 7)).isoformat(),
                "status": rng.choice(["ok", "ok", "ok", "warn", "ok", "fail"]),
                "items": rng.randint(10, 600),
            }
            for i in range(1, 9)
        ],
    }

    return {"metrics": metrics, "series": series, "tables": tables}
