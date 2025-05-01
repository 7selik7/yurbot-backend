from datetime import datetime
from pydantic import BaseModel
from uuid import UUID

from app.schemas.message_schemas import FullMessage


class CreateChat(BaseModel):
    message: str

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