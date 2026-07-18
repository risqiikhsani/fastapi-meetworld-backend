from pydantic import BaseModel, Field


class TranslationRequest(BaseModel):
    """Request body for the GenAI text translation endpoint."""

    text: str = Field(..., min_length=1, max_length=8000)
    source_lang: str | None = Field(default=None, max_length=100)
    target_lang: str = Field(..., min_length=1, max_length=100)


class TranslationResponse(BaseModel):
    """Translated text plus the language pair that was used."""

    translated_text: str
    source_lang: str | None
    target_lang: str
