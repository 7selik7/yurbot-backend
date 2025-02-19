from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class BaseUser(BaseModel):
    uuid: UUID
    email: str

class FullUser(BaseUser):
    first_name: str | None
    last_name: str | None
    avatar_url: str | None
    is_first_login: bool
    is_confirmed: bool
    created_at: datetime
    updated_at: datetime