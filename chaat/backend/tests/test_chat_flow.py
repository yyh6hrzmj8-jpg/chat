import pytest

@pytest.mark.anyio
async def test_create_session_send_message_and_history(client):
    # register
    r = await client.post("/auth/register", json={"email": "u@example.com", "password": "secret123"})
    assert r.status_code == 201

    # login (OAuth2 form)
    r = await client.post("/auth/login", data={"username": "u@example.com", "password": "secret123"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # create session
    r = await client.post("/chat/session", headers=headers)
    assert r.status_code == 201
    session_id = r.json()["session_id"]

    # send message
    r = await client.post("/chat/message", headers=headers, json={"session_id": session_id, "text": "Привет"})
    assert r.status_code == 200
    data = r.json()
    assert data["session_id"] == session_id
    assert data["user_text"] == "Привет"
    assert isinstance(data["bot_text"], str) and len(data["bot_text"]) > 0

    # history
    r = await client.get(f"/chat/history/{session_id}", headers=headers)
    assert r.status_code == 200
    hist = r.json()
    assert hist["session_id"] == session_id
    assert len(hist["messages"]) == 2
    assert hist["messages"][0]["sender"] == "user"
    assert hist["messages"][1]["sender"] == "bot"
