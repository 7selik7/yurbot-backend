from fastapi import APIRouter, Depends

from app.schemas.auth_schemas import AuthParams, TokenResponse, SignaUpParams, RefreshToken, ChangePasswordRequest, \
    SchemeResetPassword, ConfirmPasswordRequest
from app.schemas.user_schemas import FullUser

from app.services import get_auth_service
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/signup", response_model=FullUser)
async def signup(signup_data: SignaUpParams, auth_service: AuthService = Depends(get_auth_service)):
    return await auth_service.signup(signup_data)


@router.post("/login", response_model=TokenResponse)
async def login(login_data: AuthParams, auth_service: AuthService = Depends(get_auth_service)):
    return await auth_service.login(login_data)


@router.post("/forgot-password")
async def forgot_password(
        scheme_reset_password: SchemeResetPassword,
        auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.forgot_password(
        scheme_reset_password=scheme_reset_password,
    )


@router.post("/forgot-password/{token}")
async def confirm_password(
        token: str,
        request: ConfirmPasswordRequest,
        auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.confirm_password(
        token=token,
        new_password=request.new_password,
    )


@router.get("/confirmation_of_registration/{token}")
async def confirm_registration(
        token: str,
        auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.confirm_registration(
        token=token,
    )


@router.post("/change-password")
async def change_password(
        password_data: ChangePasswordRequest,
        current_user=Depends(AuthService.get_current_user),
        auth_service: AuthService = Depends(get_auth_service),
):
    await auth_service.change_password(
        user_id=current_user.uuid,
        current_password=password_data.current_password,
        new_password=password_data.new_password,
    )

    return {"message": "Password changed successfully"}


@router.post("/refresh")
async def refresh_token(refresh_token_data: RefreshToken, auth_service: AuthService = Depends(get_auth_service)):
    return await auth_service.refresh_token(token=refresh_token_data.refresh_token)


@router.get("/me", response_model=FullUser)
async def get_user_data(current_user: FullUser = Depends(AuthService.get_current_user)):
    return current_user
