from uuid import UUID

from app.models.chat_model import Chat
from app.repositories.base_repository import BaseRepository

from sqlalchemy import select

class ChatRepository(BaseRepository[Chat]):
    def __init__(self, session):
        super().__init__(session=session, model=Chat)

    async def get_chats(self, owner_uuid: UUID) -> list[Chat]:
        query = (
            select(self.model)
            .where(self.model.owner_uuid == owner_uuid)
            .where(self.model.is_deleted == False)
        )
        result = await self.session.execute(query)
        db_rows = result.scalars().all()
        return db_rows