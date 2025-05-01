from uuid import UUID

from app.models.message_model import Message
from app.repositories.base_repository import BaseRepository

from sqlalchemy import select
from sqlalchemy.orm import selectinload

class MessageRepository(BaseRepository[Message]):
    def __init__(self, session):
        super().__init__(session=session, model=Message)

    async def get_chat_messages(self, chat_uuid: UUID) -> list[Message]:
        query = (
            select(self.model)
            .options(selectinload(self.model.children))
            .where(self.model.chat_uuid == chat_uuid)
        )
        result = await self.session.execute(query)
        return result.scalars().all()
