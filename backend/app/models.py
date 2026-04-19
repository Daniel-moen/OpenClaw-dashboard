"""Pydantic schemas shared across routers."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# --- auth ---
class LoginRequest(BaseModel):
    password: str


class LoginResponse(BaseModel):
    ok: bool = True


# --- calendar ---
class EventIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    starts_at: datetime
    ends_at: datetime | None = None
    location: str | None = Field(default=None, max_length=200)
    notes: str | None = Field(default=None, max_length=2000)


class Event(EventIn):
    id: int
    created_at: datetime


# --- vault ---
class VaultFile(BaseModel):
    id: int
    name: str
    original_name: str
    mime: str
    size: int
    sha256: str
    created_at: datetime


# --- activity ---
class ActivityItem(BaseModel):
    id: int
    kind: str
    message: str
    meta: dict[str, Any] | None = None
    profile_key: str | None = None
    profile_name: str | None = None
    created_at: datetime


# --- assistant ---
class AssistantActionIn(BaseModel):
    label: str = Field(min_length=1, max_length=120)
    prompt: str = Field(min_length=1, max_length=4000)
    category: str = Field(default="general", max_length=40)


class AssistantAction(AssistantActionIn):
    id: int
    slug: str
    created_at: datetime


# --- profiles ---
class ProfileIn(BaseModel):
    name: str = Field(min_length=1, max_length=60)
    role: str = Field(default="member", max_length=40)
    emoji: str = Field(default="?", min_length=1, max_length=4)


class Profile(ProfileIn):
    id: int
    key: str
    created_at: datetime


class Me(BaseModel):
    authenticated: bool
    profile: Profile | None = None


# --- skills ---
class Skill(BaseModel):
    id: str
    name: str
    description: str
    category: str
    status: str = "available"
    source: str | None = None
    docs_url: str | None = None


# --- businesses ---
class BusinessSummary(BaseModel):
    slug: str
    name: str
    tagline: str | None = None
    status: str  # "live" | "coming-soon"
    headline: dict[str, Any] | None = None


class Metric(BaseModel):
    key: str
    label: str
    value: float | int | str
    unit: str | None = None
    delta: float | None = None
    help: str | None = None


class SeriesPoint(BaseModel):
    t: str  # ISO date or label
    v: float | int


class Series(BaseModel):
    key: str
    label: str
    points: list[SeriesPoint]


class BusinessStats(BaseModel):
    slug: str
    name: str
    fetched_at: datetime
    source: str  # "live" | "mock"
    metrics: list[Metric]
    series: list[Series] = []
    tables: dict[str, list[dict[str, Any]]] = {}
    raw: dict[str, Any] | None = None


# --- dashboard ---
class DashboardSummary(BaseModel):
    stats: list[Metric]
    recent_activity: list[ActivityItem]
    quick_actions: list[AssistantAction]
    businesses: list[BusinessSummary]
    upcoming_events: list[Event]
