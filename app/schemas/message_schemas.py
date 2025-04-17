from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from uuid import UUID

from app.enums.message_enum import MarkType, AuthorType


class FullMessage(BaseModel):
    uuid: UUID
    text: str
    mark: MarkType
    author: AuthorType
    parent_uuid: Optional[UUID] = ""
    chat_uuid: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
