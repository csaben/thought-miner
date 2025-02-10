from __future__ import annotations

from pydantic import BaseModel, Field


class Fragment(BaseModel):
    begin: str = Field(..., example="0.000")
    children: list[dict] = Field(default_factory=list)
    end: str = Field(..., example="0.000")
    id: str
    language: str | None = None
    lines: list[str] = Field(default_factory=list)


class ResponseModel(BaseModel):
    fragments: list[Fragment]
