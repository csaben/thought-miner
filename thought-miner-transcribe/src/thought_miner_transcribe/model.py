from __future__ import annotations

import uuid
from enum import IntEnum

# pydantic with enums for status: https://www.prefect.io/blog/pydantic-enums-introduction
from pydantic import BaseModel


class TranscriptStatusEnum(IntEnum):
    COMPLETED = 1
    FAILED = 2


class ResponseModel(BaseModel):
    id: uuid.UUID
    transcript: None | str
    status: TranscriptStatusEnum = TranscriptStatusEnum.FAILED
