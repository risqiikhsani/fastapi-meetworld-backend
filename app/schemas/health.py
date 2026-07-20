from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Liveness response for `GET /api/health`.

    Intentionally minimal: the route exists so the frontend can warm the
    Cloud Run instance before issuing real requests. No dependency probing
    (no OpenAI, no DB) — see the router module for the rationale.
    """

    status: Literal["ok"]
    uptime: float
    timestamp: datetime