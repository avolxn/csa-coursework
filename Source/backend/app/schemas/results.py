from __future__ import annotations

from pydantic import BaseModel, Field


class ResultPayload(BaseModel):
    user_id: int
    test_id: int
    score: int = Field(ge=0)
    max_score: int = Field(ge=1)
    comment: str = ""
