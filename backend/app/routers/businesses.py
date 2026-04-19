"""Business listing + per-business stats endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from ..businesses import get_provider, list_providers
from ..deps import require_session
from ..models import BusinessStats, BusinessSummary

router = APIRouter(
    prefix="/businesses", tags=["businesses"], dependencies=[Depends(require_session)]
)


@router.get("", response_model=list[BusinessSummary])
async def list_businesses() -> list[BusinessSummary]:
    return [await p.summary() for p in list_providers()]


@router.get("/{slug}/stats", response_model=BusinessStats)
async def business_stats(slug: str) -> BusinessStats:
    provider = get_provider(slug)
    if not provider:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"unknown business: {slug}")
    return await provider.stats()
