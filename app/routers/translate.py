from fastapi import APIRouter

from app.schemas.translate import TranslationRequest, TranslationResponse
from app.services import translate as translate_service

router = APIRouter()


@router.post("/translate", response_model=TranslationResponse, summary="Translate text with GenAI")
async def translate_endpoint(payload: TranslationRequest) -> TranslationResponse:
    translated = await translate_service.translate(
        text=payload.text,
        source_lang=payload.source_lang,
        target_lang=payload.target_lang,
    )
    return TranslationResponse(
        translated_text=translated,
        source_lang=payload.source_lang,
        target_lang=payload.target_lang,
    )
