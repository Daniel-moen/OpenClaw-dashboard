def test_jobcarver_stats_mock_when_url_unset(auth_client):
    r = auth_client.get("/api/businesses/jobcarver/stats")
    assert r.status_code == 200
    body = r.json()
    assert body["slug"] == "jobcarver"
    assert body["source"] == "mock"
    assert len(body["metrics"]) >= 4
    assert body["series"]
    assert "top_sources" in body["tables"]


def test_business_listing(auth_client):
    r = auth_client.get("/api/businesses")
    assert r.status_code == 200
    slugs = {b["slug"] for b in r.json()}
    assert {"jobcarver", "cohesionsupps"}.issubset(slugs)


def test_unknown_business(auth_client):
    r = auth_client.get("/api/businesses/nope/stats")
    assert r.status_code == 404


def test_calendar_crud(auth_client):
    r = auth_client.post(
        "/api/calendar/events",
        json={
            "title": "Team standup",
            "starts_at": "2030-01-01T10:00:00Z",
            "ends_at": "2030-01-01T10:30:00Z",
        },
    )
    assert r.status_code == 201, r.text
    eid = r.json()["id"]

    r = auth_client.get("/api/calendar/events")
    assert any(e["id"] == eid for e in r.json())

    r = auth_client.delete(f"/api/calendar/events/{eid}")
    assert r.status_code == 204


def test_skills_listing(auth_client):
    r = auth_client.get("/api/skills")
    assert r.status_code == 200
    body = r.json()
    assert len(body) >= 5
    assert {"id", "name", "category", "status"}.issubset(body[0].keys())


def test_assistant_actions_seeded(auth_client):
    r = auth_client.get("/api/assistant/actions")
    assert r.status_code == 200
    assert len(r.json()) >= 4
