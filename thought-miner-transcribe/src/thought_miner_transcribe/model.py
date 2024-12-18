from __future__ import annotations

import uuid

from pydantic import BaseModel


class ResponseModel(BaseModel):
    id: uuid.UUID
