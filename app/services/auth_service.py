from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repository import UserRepository
from app.schemas.auth_schemas import AuthParams, TokenResponse
from app.utils.jwt_service import jwt_service
from app.utils.password_service import password_service


class AuthService:
    def __init__(self, session: AsyncSession, repository: UserRepository):
        self.session = session
        self.repository = repository

    async def signup(self, signup_data: AuthParams):
        db_user = await self.repository.get_one(email=signup_data.email)
        if db_user:
            # TODO add custom exception
            raise HTTPException(status_code=500, detail="User already exists")

        signup_data.password = password_service.hash_password(signup_data.password)

        return await self.repository.create_one(signup_data.model_dump())


    async def login(self, login_data: AuthParams):
        db_user = await self.repository.get_one(email=login_data.email)

        if not db_user:
            raise HTTPException(status_code=400, detail="Email or password is incorrect")

        if not password_service.verify_password(login_data.password, db_user.password):
            raise HTTPException(status_code=400, detail="Email or password is incorrect")

        payload = {"email": db_user.email, "uuid": str(db_user.uuid)}

        return {
            "access_token": jwt_service.create_access_token(payload),
            "refresh_token": jwt_service.create_refresh_token(payload)
        }
