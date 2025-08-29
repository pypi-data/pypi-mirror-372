import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers.sessions import router as sessions_router


logger = logging.getLogger(__name__)


app = FastAPI(title="Kagebunshin API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(sessions_router, prefix="/sessions", tags=["sessions"])


