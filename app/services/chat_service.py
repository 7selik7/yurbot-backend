from collections import defaultdict

from fastapi import HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.enums.message_enum import MarkType, AuthorType
from app.models.chat_model import Chat

from app.models.message_model import Message
from app.repositories.chat_repository import ChatRepository
from app.repositories.message_repository import MessageRepository
from app.schemas.chat_schemas import FullChat
from app.schemas.message_schemas import FullMessage, SendMessage, MessageWithoutChildren, SendMessageResponse, \
    RegenerateMessage

security = HTTPBearer()

class ChatService:
    def __init__(self, session: AsyncSession, chat_repository: ChatRepository, message_repository: MessageRepository):
        self.session = session
        self.chat_repository = chat_repository
        self.message_repository = message_repository

    async def create_chat(self, message: str, owner_uuid: UUID):
        # TODO add generating chat name based on image
        new_chat = await self.chat_repository.create_one(
            data={"title": "New Chat", "is_deleted": False, "is_pinned": True, "owner_uuid": owner_uuid}
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
        msg_schema = FullMessage(**{**MessageWithoutChildren.model_validate(initial_message).model_dump(), "children": []})
        chat_schema.messages.append(msg_schema)
        return chat_schema

    async def get_chats(self, owner_uuid: UUID):
        return await self.chat_repository.get_chats(owner_uuid=owner_uuid)

    async def get_chat_messages(self, owner_uuid: UUID, chat_uuid: UUID) -> list[FullMessage]:
        await self.chat_repository.get_one_or_404(uuid=chat_uuid, owner_uuid=owner_uuid)

        raw_messages = await self.message_repository.get_chat_messages(chat_uuid=chat_uuid)

        return [
            FullMessage(
                **FullMessage.model_validate(msg).model_dump(),
                children=[child.uuid for child in msg.children]
            )
            for msg in raw_messages
        ]

    async def send_message(self, send_message_data: SendMessage, owner_uuid: UUID) -> dict:
        user_message = await self.message_repository.create_one({
            "text": send_message_data.text,
            "mark": MarkType.NONE,
            "author": AuthorType.USER,
            "parent_uuid": send_message_data.parent_uuid,
            "chat_uuid": send_message_data.chat_uuid
        })

        answer_message = await self.message_repository.create_one({
            "text": "",
            "mark": MarkType.NONE,
            "author": AuthorType.AI,
            "parent_uuid": user_message.uuid,
            "chat_uuid": send_message_data.chat_uuid
        })

        await self.chat_repository.update_one(
            model_uuid=send_message_data.chat_uuid,
            data={"uuid": send_message_data.chat_uuid}
        )

        return {
            "message": FullMessage(**{**MessageWithoutChildren.model_validate(user_message).model_dump(), "children": []}),
            "answer": FullMessage(**{**MessageWithoutChildren.model_validate(answer_message).model_dump(), "children": []}),
        }

    async def regenerate_message(self, regenerate_message_data: RegenerateMessage, owner_uuid: UUID) -> dict:
        updated_answer = await self.message_repository.update_one(
            model_uuid=regenerate_message_data.message_uuid,
            data={"text": ""}
        )

        return {
            "answer": FullMessage(
                **{**MessageWithoutChildren.model_validate(updated_answer).model_dump(), "children": []}
            ),
        }

    async def complete_answer(self, answer_uuid: UUID, text: str) -> dict:
        await self.message_repository.get_one(uuid=answer_uuid)
        updated_message = await self.message_repository.update_one(model_uuid=answer_uuid, data={"text": text})

        return FullMessage(
            **{**MessageWithoutChildren.model_validate(updated_message).model_dump(), "children": []}
        ).model_dump()

    async def update_chat_title(self, chat_uuid: UUID, new_title: str) -> Chat:
        return await self.chat_repository.update_one(model_uuid=chat_uuid, data={"title": new_title})

    async def mark_message(self, message_uuid: UUID, mark: MarkType) -> Message:
        return await self.message_repository.update_one(model_uuid=message_uuid, data={"mark": mark})

    async def delete_chat(self, chat_uuid: UUID, owner_uuid: UUID):
        db_chat = await self.chat_repository.get_one_or_404(uuid=chat_uuid)
        if db_chat.owner_uuid != owner_uuid:
            raise HTTPException(status_code=400, detail="You are not the owner of this chat")

        await self.chat_repository.update_one(model_uuid=chat_uuid, data={"is_deleted": True})

