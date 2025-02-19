from fastapi import APIRouter, Depends

from app.schemas.auth_schemas import AuthParams, TokenResponse
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

@router.post("/me")
async def get_user_data():
    return {"status_code": 200, "detail": "ok", "result": "working"}