"""Assistant skills catalog (sourced from a static JSON file)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, Depends

from ..deps import require_session
from ..models import Skill

router = APIRouter(prefix="/skills", tags=["skills"], dependencies=[Depends(require_session)])

CATALOG_PATH = Path(__file__).resolve().parent.parent / "data" / "skills.json"


@lru_cache
def _load() -> list[Skill]:
    raw = json.loads(CATALOG_PATH.read_text("utf-8"))
    return [Skill(**item) for item in raw]


@router.get("", response_model=list[Skill])
def list_skills() -> list[Skill]:
    return _load()
