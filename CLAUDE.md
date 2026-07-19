# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Stack and tooling

- Python 3.13, dependency-managed by [`uv`](https://docs.astral.sh/uv/) (`uv.lock` is committed).
- FastAPI app exposing a thin wrapper over the OpenAI Responses API and the `openai-agents` SDK. (`langchain` / `langgraph` are pulled in as deps for the skills/tooling side, but `app/` does not import them — keep it that way unless you also wire the docs router.)
- No test suite, no linter, no formatter — don't invent commands.
- CI/CD lives under `.github/workflows/`: `ci.yml` plus `deploy-{dev,staging,production}.yml`. Don't add new workflows without aligning with the existing deploy pipeline.

## Common commands

- Install / sync deps: `uv sync`
- Run the dev server: `uv run uvicorn app.main:app` (auto-reload via `fastapi[standard]` if you pass `--reload`).
- Add a dep: `uv add <pkg>` (updates `pyproject.toml` + `uv.lock`).
- After startup, `openapi.json` is written to the project root (or wherever `OPENAPI_DUMP_PATH` points). The frontend is expected to consume this file directly — change the path via `.env` if a sibling project needs it elsewhere.

## Environment

- Copy `.env.example` → `.env` and fill in `OPENAI_API_KEY`. The lifespan in `app/main.py` calls `load_dotenv()` and then `get_settings()`, so a missing key fails fast at startup.
- `.env` is gitignored; never commit it.

## Architecture

The app is a thin three-layer split under `app/`:

- `app/main.py` — FastAPI app, lifespan (loads `.env`, validates settings, dumps `openapi.json`), CORS (currently `allow_origins=["*"]` — comment in the file flags this as dev-only), router wiring. All routers are mounted under `/api`.
- `app/routers/` — one file per endpoint group (`chat.py`, `agent.py`, `stream.py`, `translate.py`). Each handler is a near-pure adapter: parse the request schema, call a service, wrap the result in the response schema (or an `EventSourceResponse` for SSE).
- `app/services/` — the actual OpenAI / agents SDK calls. Each conversation-shaped service (chat/agent/stream) defines its own `MODEL = "gpt-4o-mini"` constant — keep them in sync if you change models.
  - `chat.py` — one-shot Responses API call.
  - `agent.py` — `openai-agents` `Runner.run` for the History tutor agent.
  - `stream.py` — Responses API in `stream=True` mode; yields `{"event": "delta", "data": "{text: ...}"}` per text delta and a terminal `{"event": "done", "data": "[DONE]"}`. Non-text events are intentionally dropped.
  - `translate.py` — Responses API translation with strict structured output (`text_format=Translation`). `source_lang=None` triggers auto-detect; the model reports the detected language in `detected_source_lang`. Otherwise the source is pinned and `detected_source_lang` stays null.
- `app/services/_messages.py` — shared converter `to_responses_input(messages)` used by `chat`, `agent`, and `stream`. Maps `role="user"` to input-message items and `role="assistant"` (history echo) to output-message items — the Responses API rejects `role="assistant"` on the input side.
- `app/services/openai_client.py` — single `AsyncOpenAI` instance built via `lru_cache`; all services go through `get_async_client()`.
- `app/schemas/` — one file per domain. `chat.py` holds `ChatMessage` / `ChatRequest` / `ChatResponse`; `translate.py` holds `Translation` (the LLM's structured output shape), `TranslationRequest`, and `TranslationResponse`. Add new request/response shapes in a domain-named file rather than appending to an existing one.
- `app/config.py` — `Settings` (`pydantic-settings`) holding `openai_api_key`. Add new env-driven config here, not as ad-hoc `os.getenv` calls.

## Endpoints (mounted under `/api`)

- `POST /api/chat` — one-shot text response.
- `POST /api/agent` — runs the History tutor agent and returns its `final_output`.
- `POST /api/chat/stream` — SSE stream of text deltas, terminated by `[DONE]`.
- `POST /api/translate` — GenAI translation with strict structured output. Body is `{text, source_lang?, target_lang}`; response is `{translated_text, source_lang, target_lang, detected_source_lang}` where `detected_source_lang` is set only when `source_lang` was omitted on the request.
- `GET /` — `{"status": "ok"}` health check.

## Conventions observed in this codebase

- The frontend pulls types straight from the dumped `openapi.json`. It's regenerated on every startup by the lifespan and is committed to the repo so the frontend can vendor it without running the backend — never hand-edit it; restart the server instead.
- `web_search` tool on the Responses API call in `chat.py` is commented out — re-enable with `tools=[{"type": "web_search"}]` if needed.
- The `openai-agents` SDK uses its own internal sync client. The agent service "touches" the async client first so an unset `OPENAI_API_KEY` fails loudly rather than inside the SDK.
- Conversation endpoints are stateless: the client replays the full message history on every request (server validates the last message is `role="user"`). Don't add server-side session storage — keep that contract.

## Skills cache

`.agents/skills/` and `skills-lock.json` pin LangChain/LangGraph skills by hash. Treat the lockfile as read-only — update via the upstream `langchain-ai/langchain-skills` flow, not by hand.

## Deployment

Docker image is built via the `Dockerfile` at the repo root; CI/CD under `.github/workflows/` handles image build + deploy to dev/staging/production. Override `OPENAPI_DUMP_PATH` in `.env` if a sibling frontend project needs the schema written somewhere other than `./openapi.json`.