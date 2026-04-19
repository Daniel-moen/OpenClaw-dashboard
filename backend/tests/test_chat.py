def test_chat_status_offline_when_no_key(auth_client):
    r = auth_client.get("/api/chat/status")
    assert r.status_code == 200
    body = r.json()
    assert body["online"] is False
    assert body["model"] is None
    assert body["assistant_name"] == "Mia"


def test_chat_history_starts_empty(auth_client):
    r = auth_client.get("/api/chat/messages")
    assert r.status_code == 200
    assert r.json() == []


def test_send_offline_persists_user_and_canned_reply(auth_client):
    auth_client.post("/api/profiles/active", json={"key": "daniel"})
    r = auth_client.post("/api/chat/messages", json={"content": "Hello Mia"})
    assert r.status_code == 201
    body = r.json()
    assert body["online"] is False
    assert body["user"]["role"] == "user"
    assert body["user"]["content"] == "Hello Mia"
    assert body["user"]["profile_key"] == "daniel"
    assert body["user"]["profile_name"] == "Daniel"
    assert body["reply"]["role"] == "assistant"
    assert "offline" in body["reply"]["content"].lower()

    history = auth_client.get("/api/chat/messages").json()
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"


def test_send_rejects_blank(auth_client):
    r = auth_client.post("/api/chat/messages", json={"content": "   "})
    # Either pydantic validation (422) or our explicit empty check (400).
    assert r.status_code in (400, 422)


def test_send_truncated_at_max_length(auth_client):
    huge = "x" * 5000
    r = auth_client.post("/api/chat/messages", json={"content": huge})
    assert r.status_code == 422  # pydantic max_length


def test_clear_history(auth_client):
    auth_client.post("/api/chat/messages", json={"content": "first"})
    auth_client.post("/api/chat/messages", json={"content": "second"})
    assert len(auth_client.get("/api/chat/messages").json()) == 4

    r = auth_client.delete("/api/chat/messages")
    assert r.status_code == 204
    assert auth_client.get("/api/chat/messages").json() == []


def test_chat_requires_auth(client):
    assert client.get("/api/chat/messages").status_code == 401
    assert client.post("/api/chat/messages", json={"content": "hi"}).status_code == 401
