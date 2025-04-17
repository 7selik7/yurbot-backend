from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_session
from app.repositories.chat_repository import ChatRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.chat_service import ChatService


async def get_auth_service(session: AsyncSession = Depends(get_session)) -> AuthService:
    user_repository = UserRepository(session)
    return AuthService(session=session, repository=user_repository)

async def get_chat_service(session: AsyncSession = Depends(get_session)) -> ChatService:
    chat_repository = ChatRepository(session)
    message_repository = MessageRepository(session)
    return ChatService(session=session, chat_repository=chat_repository, message_repository=message_repository)
