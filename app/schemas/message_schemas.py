from datetime import datetime
from typing import Optional

from pydantic import BaseModel, computed_field
from uuid import UUID

from app.enums.message_enum import MarkType, AuthorType

class MessageWithoutChildren(BaseModel):
    uuid: UUID
    text: str
    mark: MarkType
    author: AuthorType
    parent_uuid: Optional[UUID] = None
    chat_uuid: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class FullMessage(BaseModel):
    uuid: UUID
    text: str
    mark: MarkType
    author: AuthorType
    parent_uuid: Optional[UUID] = None
    chat_uuid: UUID
    created_at: datetime
    updated_at: datetime
    children: list[UUID]

    class Config:
        from_attributes = True

class SendMessage(BaseModel):
    chat_uuid: UUID | None
    parent_uuid: UUID | None
    text: str

class SendMessageResponse(BaseModel):
    message: FullMessage
    answer: FullMessage
