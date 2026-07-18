from pydantic import BaseModel, Field, model_validator


class GrammarRepair(BaseModel):
    """Structured output returned by the grammar repair model.

    Either the success fields (`repaired_text` + `detected_language`) are
    populated, or `error` is populated — never both. The `model_validator`
    below enforces this so a malformed model response surfaces as a parse
    error rather than reaching the caller.
    """

    repaired_text: str | None = None
    detected_language: str | None = None
    error: str | None = None

    @model_validator(mode="after")
    def _xor_error(self) -> "GrammarRepair":
        has_error = self.error is not None
        has_repair = self.repaired_text is not None and self.detected_language is not None
        if has_error and has_repair:
            raise ValueError(
                "`error` must be mutually exclusive with `repaired_text` / "
                "`detected_language`."
            )
        if not has_error and not has_repair:
            raise ValueError(
                "Either `error` or both `repaired_text` and `detected_language` "
                "must be set."
            )
        return self


class GrammarRepairRequest(BaseModel):
    """Request body for the grammar repair endpoint."""

    text: str = Field(..., min_length=1, max_length=8000)


class GrammarRepairResponse(BaseModel):
    """Repaired text plus the detected language, or an error if detection failed."""

    repaired_text: str | None
    detected_language: str | None
    error: str | None