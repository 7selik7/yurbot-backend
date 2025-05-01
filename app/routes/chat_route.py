import asyncio

from fastapi import APIRouter, Depends, WebSocket
from uuid import UUID

from app.schemas.chat_schemas import CreateChat, FullChat
from app.schemas.message_schemas import FullMessage, SendMessage, SendMessageResponse
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
    return await chat_service.create_chat(message=chat_data.message, owner_uuid=user.uuid)


@router.get("/", response_model=list[FullChat])
async def get_chats(
    user: FullUser = Depends(AuthService.get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    return await chat_service.get_chats(owner_uuid=user.uuid)


@router.get("/{chat_uuid}/messages", response_model=list[FullMessage])
async def get_chat_messages(
    chat_uuid: UUID,
    user: FullUser = Depends(AuthService.get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    return await chat_service.get_chat_messages(owner_uuid=user.uuid, chat_uuid=chat_uuid)


@router.post("/send_message", response_model=SendMessageResponse)
async def send_message(
    send_message_data: SendMessage,
    user: FullUser = Depends(AuthService.get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
):
     return await chat_service.send_message(send_message_data=send_message_data,owner_uuid=user.uuid)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await asyncio.sleep(5)

    text = (
        "Hello! I'm your virtual assistant. "
        "I can help you analyze data, summarize documents, generate ideas, and much more. "
        "If you ever feel stuck, just ask. I'm always here to help you move forward!"
    )

    accumulated_text = ""
    for letter in text:
        accumulated_text += letter
        await websocket.send_text(accumulated_text)
        await asyncio.sleep(0.03)

    # await chats_repository.complete_answer(
    #     text=text,
    #     message_id=message_id,
    #     chat_id=chat_id,
    #     col_id=email,
    #     task_id=task_id
    # )
    # message = messages[-1].model_dump()
    # message["text"] = text
    # message_json = jsonable_encoder(message)
    # await websocket.send_json({"type": "-=close=-", "message": message_json})