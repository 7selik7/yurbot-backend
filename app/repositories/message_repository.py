from uuid import UUID

from app.models.message_model import Message
from app.repositories.base_repository import BaseRepository

from sqlalchemy import select, union_all, literal_column
from sqlalchemy.orm import selectinload,  aliased


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

    async def get_one_with_parent(self, message_uuid: UUID) -> Message:
        query = (
            select(self.model)
            .options(selectinload(self.model.parent))
            .where(self.model.uuid == message_uuid)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_message_history(self, message_uuid: UUID) -> list[Message]:
        parent_alias = aliased(self.model)

        cte = (
            select(
                self.model.uuid.label("uuid"),
                self.model.parent_uuid.label("parent_uuid"),
                literal_column("0").label("depth")
            )
            .where(self.model.uuid == message_uuid)
            .cte(name="message_cte", recursive=True)
        )

        cte_alias = aliased(cte)

        cte = cte.union_all(
            select(
                parent_alias.uuid.label("uuid"),
                parent_alias.parent_uuid.label("parent_uuid"),
                (cte_alias.c.depth + 1).label("depth")
            ).where(parent_alias.uuid == cte_alias.c.parent_uuid)
        )

        query = (
            select(self.model)
            .join(cte, self.model.uuid == cte.c.uuid)
            .options(selectinload(self.model.documents))
            .order_by(cte.c.depth.desc())
        )

        result = await self.session.execute(query)
        messages = result.scalars().unique().all()

        return messages