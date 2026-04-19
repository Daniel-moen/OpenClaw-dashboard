import io


def test_vault_requires_auth(client):
    r = client.get("/api/vault")
    assert r.status_code == 401


def test_vault_upload_list_download_delete(auth_client):
    files = {"file": ("hello.txt", io.BytesIO(b"hello world"), "text/plain")}
    r = auth_client.post("/api/vault", files=files)
    assert r.status_code == 201, r.text
    created = r.json()
    assert created["original_name"] == "hello.txt"
    assert created["size"] == len(b"hello world")
    fid = created["id"]

    r = auth_client.get("/api/vault")
    assert r.status_code == 200
    assert any(f["id"] == fid for f in r.json())

    r = auth_client.get(f"/api/vault/{fid}/download")
    assert r.status_code == 200
    assert r.content == b"hello world"
    assert r.headers["x-content-type-options"] == "nosniff"

    r = auth_client.delete(f"/api/vault/{fid}")
    assert r.status_code == 204

    r = auth_client.get(f"/api/vault/{fid}/download")
    assert r.status_code == 404


def test_vault_dedup(auth_client):
    payload = {"file": ("a.txt", io.BytesIO(b"same content"), "text/plain")}
    r1 = auth_client.post("/api/vault", files=payload)
    payload = {"file": ("b.txt", io.BytesIO(b"same content"), "text/plain")}
    r2 = auth_client.post("/api/vault", files=payload)
    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r1.json()["sha256"] == r2.json()["sha256"]
    assert r1.json()["id"] == r2.json()["id"]


def test_vault_rejects_bad_mime(auth_client):
    files = {"file": ("evil.bin", io.BytesIO(b"x"), "application/x-evil")}
    r = auth_client.post("/api/vault", files=files)
    assert r.status_code == 415


def test_vault_size_limit(auth_client, monkeypatch):
    from app import config

    config.get_settings.cache_clear()
    monkeypatch.setenv("MAX_UPLOAD_MB", "1")
    config.get_settings.cache_clear()

    big = b"x" * (2 * 1024 * 1024)
    r = auth_client.post(
        "/api/vault",
        files={"file": ("big.bin", io.BytesIO(big), "application/octet-stream")},
    )
    assert r.status_code == 413
