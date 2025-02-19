from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_session
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService


async def get_auth_service(session: AsyncSession = Depends(get_session)) -> AuthService:
    user_repository = UserRepository(session)
    return AuthService(session=session, repository=user_repository)