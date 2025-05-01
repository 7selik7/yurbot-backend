import asyncio

from fastapi import APIRouter, Depends, WebSocket
from fastapi.encoders import jsonable_encoder
from uuid import UUID

from app.db.postgres import get_session
from app.schemas.chat_schemas import CreateChat, FullChat
from app.schemas.message_schemas import FullMessage, SendMessage, SendMessageResponse, RegenerateMessage, \
    RegenerateMessageResponse
from app.schemas.user_schemas import FullUser

from app.services import get_chat_service, AuthService
from app.services.chat_service import ChatService
from app.utils.manual_dependencies import resolve_async_generator

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


@router.post("/regenerate_message", response_model=RegenerateMessageResponse)
async def send_message(
    regenerate_message_data: RegenerateMessage,
    user: FullUser = Depends(AuthService.get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
):
     return await chat_service.regenerate_message(regenerate_message_data=regenerate_message_data, owner_uuid=user.uuid)


@router.websocket("/ws/{answer_uuid}")
async def websocket_endpoint(
    answer_uuid: UUID,
    websocket: WebSocket,
):
    await websocket.accept()
    await websocket.send_json({"type": "info", "message": "Connected"})

    async with resolve_async_generator(get_session()) as session:
        chat_service: ChatService = await get_chat_service(session=session)

        await asyncio.sleep(5)

        text = (
            "Hello! I'm your virtual assistant. "
            "I can help you analyze data, summarize documents, generate ideas, and much more. "
            "If you ever feel stuck, just ask. I'm always here to help you move forward!"
        )

        accumulated_text = ""
        for letter in text:
            accumulated_text += letter
            await websocket.send_json({"type": "message", "message": accumulated_text})
            await asyncio.sleep(0.01)

        message = await chat_service.complete_answer(answer_uuid=answer_uuid, text=text)
        await websocket.send_json({"type": "close", "message": jsonable_encoder(message)})
    await websocket.close()