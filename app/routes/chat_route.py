from fastapi import APIRouter, Depends

from app.schemas.chat_schemas import CreateChat, FullChat, ChatWithoutMessages
from app.schemas.user_schemas import FullUser

from app.services import get_chat_service, AuthService
from app.services.chat_service import ChatService

router = APIRouter()


@router.post("/", response_model=FullChat)
async def create_chat(
    chat_data: CreateChat,
    user: FullUser = Depends(AuthService.get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    return await chat_service.create_chat(title=chat_data.title, message=chat_data.message, owner_id=user.uuid)


@router.get("/", response_model=list[ChatWithoutMessages])
async def get_chats(
    user: FullUser = Depends(AuthService.get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    return await chat_service.get_chats(owner_uuid=user.uuid)