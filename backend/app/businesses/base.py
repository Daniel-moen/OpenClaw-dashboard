"""Protocol implemented by every business stats provider."""

from __future__ import annotations

from typing import Protocol

from ..models import BusinessStats, BusinessSummary


class BusinessStatsProvider(Protocol):
    slug: str
    name: str
    tagline: str | None
    status: str  # "live" | "coming-soon"

    async def summary(self) -> BusinessSummary: ...

    async def stats(self) -> BusinessStats: ...
