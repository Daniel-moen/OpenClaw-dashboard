"""CohesionSupps placeholder provider.

Returns a `coming-soon` summary until the brand's stats source is wired up.
Replace `stats()` with a real implementation when ready.
"""

from __future__ import annotations

from datetime import datetime, timezone

from ..models import BusinessStats, BusinessSummary


class CohesionSuppsProvider:
    slug = "cohesionsupps"
    name = "CohesionSupps"
    tagline = "Supplements brand"
    status = "coming-soon"

    async def summary(self) -> BusinessSummary:
        return BusinessSummary(
            slug=self.slug,
            name=self.name,
            tagline=self.tagline,
            status=self.status,
            headline=None,
        )

    async def stats(self) -> BusinessStats:
        return BusinessStats(
            slug=self.slug,
            name=self.name,
            fetched_at=datetime.now(timezone.utc),
            source="mock",
            metrics=[],
            series=[],
            tables={},
            raw={"note": "CohesionSupps stats provider not yet implemented."},
        )
