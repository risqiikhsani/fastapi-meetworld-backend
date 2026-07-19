import json
import os
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import agent as agent_router
from app.routers import chat as chat_router
from app.routers import grammar as grammar_router
from app.routers import stream as stream_router
from app.routers import translate as translate_router

# Where to write the generated OpenAPI schema. Override with OPENAPI_DUMP_PATH
# in `.env` if the frontend expects it somewhere other than the project root.
DEFAULT_OPENAPI_DUMP_PATH = "openapi.json"


def _dump_openapi_schema(app: FastAPI) -> None:
    """Write app.openapi() to disk so the frontend can consume it directly."""
    target = Path(os.getenv("OPENAPI_DUMP_PATH", DEFAULT_OPENAPI_DUMP_PATH))
    try:
        target.write_text(json.dumps(app.openapi(), indent=2))
    except OSError as exc:
        print(f"[startup] WARN: failed to write OpenAPI schema to {target}: {exc}", file=sys.stderr)
        return
    print(f"[startup] OpenAPI schema written to {target.resolve()}", file=sys.stderr)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Load .env, validate settings, then emit openapi.json for the frontend."""
    load_dotenv()
    get_settings()  # raises fast if OPENAI_API_KEY or JWT_SECRET is missing
    _dump_openapi_schema(app)
    yield


app = FastAPI(
    title="MeetWorld Backend",
    description="FastAPI wrapper around OpenAI Responses API and the openai-agents SDK.",
    lifespan=lifespan,
)

# Permissive CORS for local dev — lock this down before deploying.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router.router, prefix="/api", tags=["chat"])
app.include_router(agent_router.router, prefix="/api", tags=["agent"])
app.include_router(stream_router.router, prefix="/api", tags=["stream"])
app.include_router(translate_router.router, prefix="/api", tags=["translate"])
app.include_router(grammar_router.router, prefix="/api", tags=["grammar"])


@app.get("/", tags=["health"])
def root() -> dict[str, str]:
    return {"status": "ok"}