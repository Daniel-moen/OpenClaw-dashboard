def test_login_required(client):
    r = client.get("/api/dashboard/summary")
    assert r.status_code == 401


def test_login_wrong_password(client):
    r = client.post("/api/auth/login", json={"password": "nope"})
    assert r.status_code == 401


def test_login_then_summary(auth_client):
    r = auth_client.get("/api/dashboard/summary")
    assert r.status_code == 200
    body = r.json()
    assert "stats" in body
    assert "businesses" in body


def test_logout_clears_cookie(auth_client):
    r = auth_client.post("/api/auth/logout")
    assert r.status_code == 200
    r = auth_client.get("/api/dashboard/summary")
    assert r.status_code == 401


def test_session_endpoint(auth_client):
    r = auth_client.get("/api/auth/session")
    assert r.status_code == 200
    assert r.json()["authenticated"] is True
