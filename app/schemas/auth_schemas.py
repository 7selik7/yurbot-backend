from pydantic import BaseModel

class AuthParams(BaseModel):
    email: str
    password: str


class RefreshToken(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str