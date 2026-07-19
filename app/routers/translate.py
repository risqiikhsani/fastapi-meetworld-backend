from fastapi import APIRouter

from app.schemas.translate import TranslationRequest, TranslationResponse
from app.services import translate as translate_service

router = APIRouter()


@router.post("/translate", response_model=TranslationResponse, summary="Translate text with GenAI")
async def translate_endpoint(payload: TranslationRequest) -> TranslationResponse:
    result = await translate_service.translate(
        text=payload.text,
        source_lang=payload.source_lang,
        target_lang=payload.target_lang,
    )
    return TranslationResponse(
        translated_text=result.translated_text,
        source_lang=payload.source_lang,
        target_lang=payload.target_lang,
        detected_source_lang=result.detected_source_lang,
    )
