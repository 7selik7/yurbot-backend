import json
from uuid import UUID

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID, uuid4

from app.db.postgres import get_session
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schemas import AuthParams, TokenResponse, SchemeResetPassword, UserCreateData, SignaUpParams
from app.schemas.user_schemas import FullUser
from app.services.redis_service import redis_pool
from app.services.user_email_service import user_email_service
from app.utils.jwt_service import jwt_service, JwtService
from app.utils.password_service import password_service

security = HTTPBearer()


class AuthService:
    def __init__(self, session: AsyncSession, repository: UserRepository):
        self.session = session
        self.repository = repository

    async def signup(self, signup_data: SignaUpParams):
        db_user = await self.repository.get_one(email=signup_data.email)
        if db_user:
            # TODO add custom exception
            raise HTTPException(status_code=404, detail="User already exists")

        signup_data.password = password_service.hash_password(signup_data.password)

        user_create_data = UserCreateData(
            email=signup_data.email,
            password=signup_data.password,
        )

        new_user = await self.repository.create_one(user_create_data.model_dump())

        confirmation_token = str(uuid4())

        redis = await redis_pool.get_redis()
        token_data = {
            "email": new_user.email,
        }
        token_key = f"confirmation_token:{confirmation_token}"
        token_expiration = 3600
        await redis.setex(token_key, token_expiration, json.dumps(token_data))

        url = f"{signup_data.host}/confirmation_of_registration/{confirmation_token}"

        await user_email_service.send_signup_confirmation(email=new_user.email, url=url)

        return new_user

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

    async def change_password(self, user_id: UUID, current_password: str, new_password: str) -> bool:
        db_user = await self.repository.get_one(uuid=user_id)

        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        if not password_service.verify_password(current_password, db_user.password):
            raise HTTPException(status_code=400, detail="Current password is incorrect")

        hashed_password = password_service.hash_password(new_password)

        try:
            await self.repository.update_one(
                model_uuid=db_user.uuid,
                data={'password': hashed_password}
            )
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update password: {str(e)}")

    async def get_user_by_email(self, email: str):
        db_user = await self.repository.get_one(email=email)
        if not db_user:
            raise HTTPException(
                status_code=404,
                detail="User not found",
            )
        return db_user

    async def forgot_password(self, scheme_reset_password: SchemeResetPassword):
        print(f'{scheme_reset_password.host} Forgot password: {scheme_reset_password.email}')
        redis = await redis_pool.get_redis()
        key = f"password_reset_limit:{scheme_reset_password.email}"
        limit_duration = 600
        token_expiration = 3600

        if await redis.exists(key):
            raise HTTPException(
                status_code=429,
                detail="Too many password reset requests. Try again after 10 minutes.",
            )
        else:
            await redis.setex(key, limit_duration, key)

        user = await self.get_user_by_email(scheme_reset_password.email)
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found.",
            )

        reset_token = uuid4().hex
        token_key = f"password_reset_token:{reset_token}"
        token_data = {
            "email": scheme_reset_password.email,
        }
        await redis.setex(token_key, token_expiration, json.dumps(token_data))

        url = f"{scheme_reset_password.host}/forgot-password/{reset_token}"
        await user_email_service.send_reset_password(email=scheme_reset_password.email, url=url)

        return {"detail": "Password reset email sent"}

    async def confirm_password(self, token: str, new_password: str):
        redis = await redis_pool.get_redis()
        token_key = f"password_reset_token:{token}"

        token_data_str = await redis.get(token_key)
        if not token_data_str:
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired token.",
            )

        try:
            token_data = json.loads(token_data_str)
            email = token_data["email"]
        except (json.JSONDecodeError, KeyError):
            raise HTTPException(
                status_code=400,
                detail="Invalid token data.",
            )

        user = await self.repository.get_one(email=email)
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found.",
            )

        hashed_password = password_service.hash_password(new_password)

        try:
            await self.repository.update_one(
                model_uuid=user.uuid,
                data={'password': hashed_password}
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update password: {str(e)}",
            )

        await redis.delete(token_key)
        return {"detail": "Password updated successfully."}

    async def confirm_registration(self, token: str):

        redis = await redis_pool.get_redis()
        token_key = f"confirmation_token:{token}"

        token_data_str = await redis.get(token_key)
        if not token_data_str:
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired confirmation token.",
            )

        try:
            token_data = json.loads(token_data_str)
            email = token_data["email"]
        except (json.JSONDecodeError, KeyError):
            raise HTTPException(
                status_code=400,
                detail="Invalid token data.",
            )

        user = await self.repository.get_one(email=email)
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found.",
            )

        try:
            await self.repository.update_one(
                model_uuid=user.uuid,
                data={'is_confirmed': True}
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update user confirmation status: {str(e)}",
            )

        await redis.delete(token_key)

        return {"detail": "Registration confirmed successfully."}

    @staticmethod
    async def get_current_user(
            token: HTTPAuthorizationCredentials = Depends(security),
            session: AsyncSession = Depends(get_session)
    ) -> FullUser:
        decoded_token = JwtService.verify_jwt_token(token=token.credentials)
        if not decoded_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        user_repository = UserRepository(session=session)
        db_user = await user_repository.get_one(email=decoded_token.get("email"))
        return FullUser.model_validate(db_user)
