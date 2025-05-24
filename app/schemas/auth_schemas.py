from pydantic import BaseModel


class UserCreateData(BaseModel):
    email: str
    password: str


class AuthParams(BaseModel):
    email: str
    password: str


class SignaUpParams(BaseModel):
    email: str
    password: str
    host: str


class RefreshToken(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class SchemeResetPassword(BaseModel):
    email: str
    host: str


class ConfirmPasswordRequest(BaseModel):
    new_password: str
