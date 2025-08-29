import asyncio
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Optional, Set, Any
from uuid import uuid4

from fastapi import WebSocket
from playwright.async_api import async_playwright, BrowserContext

from ...config.settings import (
    BROWSER_EXECUTABLE_PATH,
    USER_DATA_DIR,
    DEFAULT_PERMISSIONS,
    ACTUAL_VIEWPORT_WIDTH,
    ACTUAL_VIEWPORT_HEIGHT,
    GROUPCHAT_ROOM,
    ENABLE_SUMMARIZATION,
    MAX_KAGEBUNSHIN_INSTANCES,
)
from ...automation.fingerprinting import get_stealth_browser_args, apply_fingerprint_profile_to_context
from ...core.agent import KageBunshinAgent
from ...tools.delegation import get_additional_tools
from ...utils import generate_agent_name, normalize_chat_content


logger = logging.getLogger(__name__)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Session:
    id: str
    context: BrowserContext
    orchestrator: KageBunshinAgent
    inbox: "asyncio.Queue[str]" = field(default_factory=asyncio.Queue)
    listeners: Set[WebSocket] = field(default_factory=set)
    status: str = "idle"  # idle|running|closed
    last_activity_at: str = field(default_factory=_utc_now_iso)
    bg_task: Optional[asyncio.Task] = None


class SessionManager:
    def __init__(self, max_sessions: int = MAX_KAGEBUNSHIN_INSTANCES):
        self._sessions: Dict[str, Session] = {}
        self._sem = asyncio.Semaphore(max_sessions)
        self._lock = asyncio.Lock()
        self._playwright = None

    async def _ensure_playwright(self):
        if self._playwright is None:
            self._playwright = await async_playwright().start()

    async def create_session(
        self,
        first_query: Optional[str] = None,
        headless: Optional[bool] = None,
        viewport_width: Optional[int] = None,
        viewport_height: Optional[int] = None,
        user_data_dir: Optional[str] = None,
    ) -> str:
        await self._ensure_playwright()
        async with self._sem:
            session_id = uuid4().hex

            launch_options: Dict[str, Any] = {
                "headless": False if headless is None else headless,
                "args": get_stealth_browser_args(),
                "ignore_default_args": ["--enable-automation"],
            }
            if BROWSER_EXECUTABLE_PATH:
                launch_options["executable_path"] = BROWSER_EXECUTABLE_PATH
            else:
                launch_options["channel"] = "chrome"

            # Choose persistent or ephemeral context
            ctx_dir = os.path.expanduser(user_data_dir) if user_data_dir else (os.path.expanduser(USER_DATA_DIR) if USER_DATA_DIR else None)
            if ctx_dir:
                context = await self._playwright.chromium.launch_persistent_context(
                    ctx_dir,
                    **launch_options,
                    permissions=DEFAULT_PERMISSIONS,
                )
            else:
                browser = await self._playwright.chromium.launch(**launch_options)
                context = await browser.new_context(
                    permissions=DEFAULT_PERMISSIONS,
                    viewport={"width": viewport_width or ACTUAL_VIEWPORT_WIDTH, "height": viewport_height or ACTUAL_VIEWPORT_HEIGHT},
                )

            # Fingerprint profile
            try:
                profile = await apply_fingerprint_profile_to_context(context)
                try:
                    await context.add_init_script(
                        f"Object.defineProperty(navigator, 'userAgent', {{ get: () => '{profile['user_agent']}' }});"
                    )
                except Exception:
                    pass
            except Exception:
                pass

            # Orchestrator
            agent_name = generate_agent_name()
            tools = get_additional_tools(context, username=agent_name, group_room=GROUPCHAT_ROOM)
            orchestrator = await KageBunshinAgent.create(
                context,
                additional_tools=tools,
                group_room=GROUPCHAT_ROOM,
                username=agent_name,
                enable_summarization=ENABLE_SUMMARIZATION,
            )

            session = Session(
                id=session_id,
                context=context,
                orchestrator=orchestrator,
            )

            # Background worker
            session.bg_task = asyncio.create_task(self._session_worker(session))

            # Prime with first query
            if first_query:
                await session.inbox.put(first_query)

            async with self._lock:
                self._sessions[session_id] = session

            return session_id

    async def _broadcast(self, session: Session, payload: dict) -> None:
        to_remove: Set[WebSocket] = set()
        for ws in list(session.listeners):
            try:
                await ws.send_json(payload)
            except Exception:
                to_remove.add(ws)
        session.listeners.difference_update(to_remove)

    async def _session_worker(self, session: Session) -> None:
        try:
            while session.status != "closed":
                text = await session.inbox.get()
                session.status = "running"
                session.last_activity_at = _utc_now_iso()
                await self._broadcast(session, {"type": "phase", "text": "Starting streaming automation..."})
                last_agent_message = ""
                try:
                    async for chunk in session.orchestrator.astream(text):
                        if 'agent' in chunk:
                            for msg in chunk['agent'].get('messages', []):
                                if hasattr(msg, 'content') and msg.content:
                                    content = normalize_chat_content(msg.content)
                                    last_agent_message = content
                                    await self._broadcast(session, {"type": "message", "role": "agent", "text": content})
                                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                                    for call in msg.tool_calls:
                                        name = call.get('name', 'unknown')
                                        args = call.get('args', {})
                                        await self._broadcast(session, {"type": "tool", "name": name, "args": args})
                        if 'summarizer' in chunk:
                            for msg in chunk['summarizer'].get('messages', []):
                                if hasattr(msg, 'content') and msg.content:
                                    await self._broadcast(session, {"type": "message", "role": "summarizer", "text": normalize_chat_content(msg.content)})

                    if last_agent_message:
                        await self._broadcast(session, {"type": "final", "text": last_agent_message})
                        current_url = await session.orchestrator.get_current_url()
                        current_title = await session.orchestrator.get_current_title()
                        action_count = session.orchestrator.get_action_count()
                        await self._broadcast(session, {"type": "success", "final_url": current_url, "final_title": current_title, "actions": action_count})
                    else:
                        try:
                            extracted = session.orchestrator._extract_final_answer()  # type: ignore[attr-defined]
                            if extracted:
                                await self._broadcast(session, {"type": "final", "text": extracted})
                            else:
                                await self._broadcast(session, {"type": "error", "text": "No final answer was provided."})
                        except Exception:
                            await self._broadcast(session, {"type": "error", "text": "No final answer was provided."})
                except Exception as e:
                    await self._broadcast(session, {"type": "error", "text": str(e)})
                finally:
                    session.status = "idle"
                    session.last_activity_at = _utc_now_iso()
        except asyncio.CancelledError:
            pass

    async def attach_listener(self, session_id: str, ws: WebSocket) -> None:
        session = self._sessions.get(session_id)
        if not session:
            raise KeyError("Session not found")
        session.listeners.add(ws)

    async def send_prompt(self, session_id: str, text: str) -> None:
        session = self._sessions.get(session_id)
        if not session:
            raise KeyError("Session not found")
        await session.inbox.put(text)
        session.last_activity_at = _utc_now_iso()

    async def get_status(self, session_id: str) -> dict:
        session = self._sessions.get(session_id)
        if not session:
            raise KeyError("Session not found")
        try:
            current_url = await session.orchestrator.get_current_url()
            current_title = await session.orchestrator.get_current_title()
            actions = session.orchestrator.get_action_count()
        except Exception:
            current_url = None
            current_title = None
            actions = None
        return {
            "session_id": session.id,
            "status": session.status,
            "last_activity_at": session.last_activity_at,
            "current_url": current_url,
            "current_title": current_title,
            "actions_performed": actions,
        }

    async def close(self, session_id: str) -> None:
        session = self._sessions.pop(session_id, None)
        if not session:
            return
        session.status = "closed"
        try:
            if session.bg_task:
                session.bg_task.cancel()
        except Exception:
            pass
        try:
            session.orchestrator.dispose()
        except Exception:
            pass
        try:
            await session.context.close()
        except Exception:
            pass


_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    global _manager
    if _manager is None:
        _manager = SessionManager()
    return _manager


