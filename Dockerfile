# syntax=docker/dockerfile:1.7
#
# Multi-stage build for the FastAPI service that powers meetworld.
#
# - builder: uses uv to resolve uv.lock into a venv (deps only, no project
#   install yet). Source is layered on top so dep resolution is cached.
# - runtime: copies the venv + source into a slim base image and starts
#   uvicorn on Cloud Run's injected $PORT (default 8080).
#
# Build:    docker build -t meetworld-backend:dev .
# Run:      docker run --rm -p 8080:8080 -e OPENAI_API_KEY=sk-... meetworld-backend:dev
# Health:   curl -fsS http://localhost:8080/

# ---------- builder ----------------------------------------------------------
FROM python:3.13-slim-bookworm AS builder

# Pull uv from the official image. `latest` tracks the current stable uv
# release; pin to a specific tag (e.g. ghcr.io/astral-sh/uv:0.5.11) if you
# need bit-for-bit reproducible builds.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# uv knobs:
#   UV_LINK_MODE=copy         -> hard-copy files into the venv so the
#                                COPY --from=builder boundary works
#                                (default symlinks would dangle across stages).
#   UV_COMPILE_BYTECODE=1     -> precompile .pyc (faster cold start).
#   UV_PYTHON_DOWNLOADS=never -> use the system Python 3.13; don't fetch
#                                another one.
#   PYTHONDONTWRITEBYTECODE=1 -> don't drop stray .pyc into /app on COPY.
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Copy the lockfile first so the deps layer caches independently of source
# edits. `uv sync` will fail (not warn) if pyproject.toml and uv.lock drift.
COPY pyproject.toml uv.lock ./

# --frozen:    fail if uv.lock is out of sync with pyproject.toml.
# --no-dev:    no test/lint tooling in this repo (see CLAUDE.md).
# --no-install-project: install deps only; the `app/` package is found via
#                        cwd at runtime, so it doesn't need to be installed
#                        into the venv.
RUN uv sync --frozen --no-dev --no-install-project

# Now layer the application source on top of the cached venv.
COPY app ./app


# ---------- runtime ----------------------------------------------------------
FROM python:3.13-slim-bookworm

# Cloud Run prefers (and newer revisions require) non-root containers. Create
# the user before COPY so we can set ownership in one shot via --chown.
RUN groupadd --system --gid 1000 app \
    && useradd --system --uid 1000 --gid app --no-create-home --shell /bin/false app

# Keep `uv` in the runtime image for `docker exec`/debug sessions. Drop this
# line if you want the smallest possible image (you'll need to invoke
# uvicorn via /app/.venv/bin/python -m uvicorn instead).
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

# Pull the venv + source from the builder. --chown sets ownership to the
# non-root user we just created, so the app/ dir is writable for the
# lifespan's openapi.json dump.
COPY --from=builder --chown=app:app /app /app

WORKDIR /app

# Activate the venv by default and stream logs to stdout/stderr without
# buffering (so Cloud Run logs surface immediately).
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER app

# Cloud Run sends traffic on $PORT (defaults to 8080). The EXPOSE here is
# documentation; Cloud Run does not actually consume it.
EXPOSE 8080

# sh -c so ${PORT:-8080} expands at runtime, not at image-build time.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]