from datetime import UTC, datetime
from time import monotonic

from fastapi import APIRouter

from app.schemas.health import HealthResponse

router = APIRouter()

# Captured at module load so `uptime` is monotonic process uptime, not
# wall-clock. System clock adjustments (NTP, manual changes) would
# otherwise produce negative or jumping values.
_STARTED_AT = monotonic()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Liveness probe used to warm the Cloud Run instance",
)
async def health_endpoint() -> HealthResponse:
    """Cheap public probe — no auth, no upstream calls, no body.

    Mirrors the common top-level fields of the NestJS `/api/health`
    response (`status`, `uptime`, `timestamp`) so the frontend can render
    both backends against a shared contract. NestJS extends this base
    with `database` and `redis` dependency checks; FastAPI has neither,
    so it does not.
    """
    return HealthResponse(
        status="ok",
        uptime=monotonic() - _STARTED_AT,
        timestamp=datetime.now(UTC),
    )