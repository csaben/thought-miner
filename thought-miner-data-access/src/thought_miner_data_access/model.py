from __future__ import annotations

from enum import IntEnum
from uuid import UUID

# pydantic with enums for status: https://www.prefect.io/blog/pydantic-enums-introduction
from pydantic import BaseModel


class StatusEnum(IntEnum):
    COMPLETED = (1,)
    FAILED = (2,)


class Status(BaseModel):
    id: UUID
    status: StatusEnum
