import io


def test_profiles_seeded(auth_client):
    r = auth_client.get("/api/profiles")
    assert r.status_code == 200
    keys = {p["key"] for p in r.json()}
    assert {"daniel", "partner"}.issubset(keys)


def test_active_profile_default_none(auth_client):
    r = auth_client.get("/api/profiles/active")
    assert r.status_code == 200
    assert r.json() is None


def test_set_active_profile_and_me(auth_client):
    r = auth_client.post("/api/profiles/active", json={"key": "daniel"})
    assert r.status_code == 200
    assert r.json()["key"] == "daniel"

    r = auth_client.get("/api/me")
    assert r.status_code == 200
    body = r.json()
    assert body["authenticated"] is True
    assert body["profile"]["key"] == "daniel"
    assert body["profile"]["name"] == "Daniel"


def test_unknown_profile_rejected(auth_client):
    r = auth_client.post("/api/profiles/active", json={"key": "ghost"})
    assert r.status_code == 404


def test_rename_profile(auth_client):
    profiles = auth_client.get("/api/profiles").json()
    partner = next(p for p in profiles if p["key"] == "partner")
    r = auth_client.put(
        f"/api/profiles/{partner['id']}",
        json={"name": "Alex", "role": "co-founder", "emoji": "A"},
    )
    assert r.status_code == 200
    assert r.json()["name"] == "Alex"
    assert r.json()["emoji"] == "A"


def test_activity_tagged_with_profile(auth_client):
    auth_client.post("/api/profiles/active", json={"key": "partner"})
    auth_client.post(
        "/api/vault",
        files={"file": ("hi.txt", io.BytesIO(b"hi"), "text/plain")},
    )
    summary = auth_client.get("/api/dashboard/summary").json()
    upload_events = [a for a in summary["recent_activity"] if a["kind"] == "vault.upload"]
    assert upload_events, "expected upload activity"
    assert upload_events[0]["profile_key"] == "partner"
    assert upload_events[0]["profile_name"] == "Partner"


def test_me_unauthenticated(client):
    r = client.get("/api/me")
    assert r.status_code == 200
    body = r.json()
    assert body["authenticated"] is False
    assert body["profile"] is None
