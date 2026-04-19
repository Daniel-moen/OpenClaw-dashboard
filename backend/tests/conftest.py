"""Shared pytest fixtures."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolated_data(tmp_path: Path, monkeypatch):
    """Each test gets a fresh data dir + sqlite db + uploads."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    monkeypatch.setenv("DATA_DIR", str(data_dir))
    monkeypatch.setenv("ADMIN_PASSWORD", "test-password")
    monkeypatch.setenv("SESSION_SECRET", "test-secret-must-be-long-enough-1234567890")
    monkeypatch.setenv("FRONTEND_ORIGIN", "http://testserver")

    # Reset cached settings + db connection so they pick up the new env vars.
    from app import config, db, security

    config.get_settings.cache_clear()
    db.reset_connection_for_tests(data_dir / "app.db")
    # Fresh login rate-limit bucket per test.
    security.login_limiter = security.LoginLimiter()

    yield

    config.get_settings.cache_clear()
    if data_dir.exists():
        shutil.rmtree(data_dir, ignore_errors=True)


@pytest.fixture
def client():
    from fastapi.testclient import TestClient

    from app.main import create_app

    app = create_app()
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_client(client):
    r = client.post("/api/auth/login", json={"password": "test-password"})
    assert r.status_code == 200, r.text
    return client
