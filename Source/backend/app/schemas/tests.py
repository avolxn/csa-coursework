from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class TestPayload(BaseModel):
    title: str
    subject: str
    description: str = ""
    pass_percent: int = Field(default=60, ge=1, le=100)

    @field_validator("title", "subject")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Поле не должно быть пустым")
        return cleaned
