from pydantic import BaseModel, Field


class Translation(BaseModel):
    """Structured output returned by the translation model.

    `detected_source_lang` is populated only when the caller did not pin
    `source_lang` on the request, so the model can report what it inferred.
    """

    translated_text: str
    detected_source_lang: str | None = None


class TranslationRequest(BaseModel):
    """Request body for the GenAI text translation endpoint."""

    text: str = Field(..., min_length=1, max_length=8000)
    source_lang: str | None = Field(default=None, max_length=100)
    target_lang: str = Field(..., min_length=1, max_length=100)


class TranslationResponse(BaseModel):
    """Translated text plus the language pair that was used.

    `source_lang` echoes whatever was passed in (may be None for auto-detect).
    `detected_source_lang` is set only when auto-detection ran.
    """

    translated_text: str
    source_lang: str | None
    target_lang: str
    detected_source_lang: str | None = None
