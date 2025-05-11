from uuid import UUID

from datetime import datetime
from pydantic import BaseModel


class Document(BaseModel):
    uuid: UUID
    name: str
    url: str
    mime_type: str
    size: str
    message_uuid: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
