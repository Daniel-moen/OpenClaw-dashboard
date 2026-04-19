"""Business stats registry. Add new brands here."""

from __future__ import annotations

from .base import BusinessStatsProvider
from .cohesionsupps import CohesionSuppsProvider
from .jobcarver import JobCarverProvider

_REGISTRY: dict[str, BusinessStatsProvider] = {}


def _register(provider: BusinessStatsProvider) -> None:
    _REGISTRY[provider.slug] = provider


_register(JobCarverProvider())
_register(CohesionSuppsProvider())


def list_providers() -> list[BusinessStatsProvider]:
    return list(_REGISTRY.values())


def get_provider(slug: str) -> BusinessStatsProvider | None:
    return _REGISTRY.get(slug)
