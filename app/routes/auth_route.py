from fastapi import APIRouter, Depends

from app.schemas.auth_schemas import AuthParams, TokenResponse, RefreshToken
from app.schemas.user_schemas import FullUser

from app.services import get_auth_service
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/signup", response_model=FullUser)
async def signup(signup_data: AuthParams, auth_service: AuthService = Depends(get_auth_service)):
    return await auth_service.signup(signup_data)

@router.post("/login", response_model=TokenResponse)
async def login(login_data: AuthParams, auth_service: AuthService = Depends(get_auth_service)):
    return await auth_service.login(login_data)

@router.post("/forgot_password")
async def forgot_password():
    return {"status_code": 200, "detail": "ok", "result": "working"}

@router.post("/reset_password")
async def reset_password():
    return {"status_code": 200, "detail": "ok", "result": "working"}

@router.post("/refresh")
async def refresh_token(refresh_token_data: RefreshToken, auth_service: AuthService = Depends(get_auth_service)):
    return await auth_service.refresh_token(token=refresh_token_data.refresh_token)

@router.get("/me", response_model=FullUser)
async def get_user_data(current_user: FullUser = Depends(AuthService.get_current_user)):
    return current_user