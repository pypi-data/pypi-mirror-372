import logging
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from ..schemas import CreateSessionRequest, CreateSessionResponse, SendMessageRequest, SessionStatus
from ..services.session_manager import get_session_manager


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("", response_model=CreateSessionResponse)
async def create_session(payload: CreateSessionRequest):
    mgr = get_session_manager()
    sid = await mgr.create_session(
        first_query=payload.first_query,
        headless=payload.headless,
        viewport_width=payload.viewport_width,
        viewport_height=payload.viewport_height,
        user_data_dir=payload.user_data_dir,
    )
    return CreateSessionResponse(session_id=sid)


@router.websocket("/{session_id}/stream")
async def stream_session(ws: WebSocket, session_id: str):
    await ws.accept()
    mgr = get_session_manager()
    try:
        await mgr.attach_listener(session_id, ws)
        while True:
            data = await ws.receive_json()
            if not isinstance(data, dict):
                continue
            t = data.get("type")
            if t == "user_message":
                text = data.get("text", "")
                if text:
                    await mgr.send_prompt(session_id, text)
            # ignore unknown payloads
    except WebSocketDisconnect:
        return
    except KeyError:
        await ws.close(code=4404)
    except Exception as e:
        try:
            await ws.send_json({"type": "error", "text": str(e)})
        except Exception:
            pass
        await ws.close()


@router.post("/{session_id}/messages")
async def send_message(session_id: str, payload: SendMessageRequest):
    mgr = get_session_manager()
    try:
        await mgr.send_prompt(session_id, payload.text)
        return {"status": "accepted"}
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")


@router.get("/{session_id}", response_model=SessionStatus)
async def get_status(session_id: str):
    mgr = get_session_manager()
    try:
        data = await mgr.get_status(session_id)
        return SessionStatus(**data)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")


@router.delete("/{session_id}")
async def delete_session(session_id: str):
    mgr = get_session_manager()
    await mgr.close(session_id)
    return {"status": "closed"}


