import asyncio
import types
from typing import Any, Dict, Optional

import pytest
from fastapi.testclient import TestClient

from kagebunshin.api.main import app


class FakeSessionManager:
    def __init__(self) -> None:
        self._ws = None
        self._closed = False
        self._last_prompt: Optional[str] = None

    async def create_session(
        self,
        first_query: Optional[str] = None,
        headless: Optional[bool] = None,
        viewport_width: Optional[int] = None,
        viewport_height: Optional[int] = None,
        user_data_dir: Optional[str] = None,
    ) -> str:
        return "test-session-id"

    async def attach_listener(self, session_id: str, ws) -> None:
        self._ws = ws

    async def send_prompt(self, session_id: str, text: str) -> None:
        self._last_prompt = text
        # Immediately echo a fake final event to client if WS attached
        if self._ws is not None:
            await self._ws.send_json({"type": "final", "text": "ok"})

    async def get_status(self, session_id: str) -> Dict[str, Any]:
        return {
            "session_id": session_id,
            "status": "idle",
            "last_activity_at": "2025-01-01T00:00:00Z",
            "current_url": "about:blank",
            "current_title": "Blank",
            "actions_performed": 0,
        }

    async def close(self, session_id: str) -> None:
        self._closed = True


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    # Patch the router-level getter to use our fake manager instance
    from kagebunshin.api.routers import sessions as sessions_router

    fake_mgr = FakeSessionManager()
    monkeypatch.setattr(sessions_router, "get_session_manager", lambda: fake_mgr)
    return TestClient(app)


def test_health_ok(client: TestClient):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_create_session(client: TestClient):
    res = client.post("/sessions", json={"first_query": None})
    assert res.status_code == 200
    data = res.json()
    assert "session_id" in data and data["session_id"] == "test-session-id"


def test_get_status(client: TestClient):
    sid = "abc"
    res = client.get(f"/sessions/{sid}")
    assert res.status_code == 200
    data = res.json()
    assert data["session_id"] == sid
    assert data["status"] == "idle"


def test_send_message_rest(client: TestClient):
    sid = "abc"
    res = client.post(f"/sessions/{sid}/messages", json={"text": "hello"})
    assert res.status_code == 200
    assert res.json()["status"] == "accepted"


def test_websocket_stream_echo_final_event(client: TestClient):
    sid = "ws1"
    with client.websocket_connect(f"/sessions/{sid}/stream") as ws:
        # Send a user message; fake manager will echo a final event immediately
        ws.send_json({"type": "user_message", "text": "run"})
        event = ws.receive_json()
        assert event["type"] == "final"
        assert event["text"] == "ok"


