from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_session
from app.models.user_model import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schemas import AuthParams, TokenResponse
from app.utils.jwt_service import jwt_service, JwtService
from app.utils.password_service import password_service


security = HTTPBearer()

class AuthService:
    def __init__(self, session: AsyncSession, repository: UserRepository):
        self.session = session
        self.repository = repository

    async def signup(self, signup_data: AuthParams):
        db_user = await self.repository.get_one(email=signup_data.email)
        if db_user:
            # TODO add custom exception
            raise HTTPException(status_code=404, detail="User already exists")

        signup_data.password = password_service.hash_password(signup_data.password)

        return await self.repository.create_one(signup_data.model_dump())


    async def login(self, login_data: AuthParams) -> TokenResponse:
        db_user = await self.repository.get_one(email=login_data.email)

        if not db_user:
            raise HTTPException(status_code=400, detail="Email or password is incorrect")

        if not password_service.verify_password(login_data.password, db_user.password):
            raise HTTPException(status_code=400, detail="Email or password is incorrect")

        payload = {"email": db_user.email, "uuid": str(db_user.uuid)}

        return TokenResponse(
            access_token=jwt_service.create_access_token(payload=payload),
            refresh_token=jwt_service.create_refresh_token(payload=payload)
        )

    async def refresh_token(self, token: str):
        decoded_token = JwtService.verify_jwt_token(token=token)
        payload = {"email": decoded_token.get("email"), "uuid": decoded_token.get("uuid")}

        return TokenResponse(
            access_token=jwt_service.create_access_token(payload=payload),
            refresh_token=token
        )

    @staticmethod
    async def get_current_user(
        token: HTTPAuthorizationCredentials = Depends(security),
        session: AsyncSession = Depends(get_session)
    ) -> User:
        decoded_token = JwtService.verify_jwt_token(token=token.credentials)
        if not decoded_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        user_repository = UserRepository(session=session)
        return await user_repository.get_one(email=decoded_token.get("email"))