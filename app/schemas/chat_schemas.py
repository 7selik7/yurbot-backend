from datetime import datetime
from pydantic import BaseModel
from uuid import UUID

from app.schemas.message_schemas import FullMessage


class CreateChat(BaseModel):
    title: str
    message: str


class ChatWithoutMessages(BaseModel):
    uuid: UUID
    title: str
    is_pinned: bool
    owner_uuid: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FullChat(BaseModel):
    uuid: UUID
    title: str
    is_pinned: bool
    owner_uuid: UUID
    messages: list[FullMessage] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True