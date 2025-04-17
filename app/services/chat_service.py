from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.enums.message_enum import MarkType, AuthorType
from app.models.chat_model import Chat
from app.repositories import chat_repository
from app.repositories.chat_repository import ChatRepository
from app.repositories.message_repository import MessageRepository
from app.schemas.chat_schemas import FullChat
from app.schemas.message_schemas import FullMessage

security = HTTPBearer()

class ChatService:
    def __init__(self, session: AsyncSession, chat_repository: ChatRepository, message_repository: MessageRepository):
        self.session = session
        self.chat_repository = chat_repository
        self.message_repository = message_repository

    async def create_chat(self, title: str, message: str, owner_id: UUID):
        # TODO add generating chat name based on image
        new_chat = await self.chat_repository.create_one(
            data={"title": title, "is_deleted": False, "is_pinned": True, "owner_uuid": owner_id}
        )
        initial_message = await self.message_repository.create_one({
            "text": "",
            "mark": MarkType.NONE,
            "author": AuthorType.AI,
            "parent_uuid": None,
            "chat_uuid": new_chat.uuid
        })

        chat_dict = new_chat.__dict__.copy()
        chat_dict["messages"] = []

        chat_schema = FullChat(**chat_dict)
        msg_schema = FullMessage.model_validate(initial_message)
        chat_schema.messages.append(msg_schema)
        return chat_schema

    async def get_chats(self, owner_uuid: UUID):
        return await self.chat_repository.get_chats(owner_uuid=owner_uuid)
