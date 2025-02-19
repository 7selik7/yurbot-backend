import jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException

from app.core.config import settings

class JwtService:
    def create_access_token(self, payload: dict) -> str:
        expiration = self.get_expiration_time(minutes=10)
        return jwt.encode({**payload, "exp": expiration}, settings.JWT_SECRET_KEY, algorithm="HS256")

    def create_refresh_token(self, payload: dict) -> str:
        expiration = self.get_expiration_time(days=7)
        return jwt.encode({**payload, "exp": expiration}, settings.JWT_SECRET_KEY, algorithm="HS256")

    @staticmethod
    def get_expiration_time(**params) -> datetime:
        return datetime.now(timezone.utc) + timedelta(**params)

    @staticmethod
    def verify_jwt_token(token: str) -> dict:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
            if not payload:
                raise HTTPException(status_code=401, detail="Token is empty")
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

jwt_service = JwtService()
