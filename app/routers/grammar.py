from fastapi import APIRouter

from app.schemas.grammar import GrammarRepairRequest, GrammarRepairResponse
from app.services import grammar as grammar_service

router = APIRouter()


@router.post(
    "/grammar/repair",
    response_model=GrammarRepairResponse,
    summary="Repair grammar in place with GenAI (auto-detects the language)",
)
async def grammar_repair_endpoint(
    payload: GrammarRepairRequest,
) -> GrammarRepairResponse:
    result = await grammar_service.repair_grammar(payload.text)
    return GrammarRepairResponse(
        repaired_text=result.repaired_text,
        detected_language=result.detected_language,
        error=result.error,
    )