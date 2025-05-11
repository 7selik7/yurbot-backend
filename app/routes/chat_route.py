import asyncio
import json
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, WebSocket, Form, UploadFile, File
from fastapi.encoders import jsonable_encoder
from uuid import UUID

from app.db.postgres import get_session
from app.schemas.chat_schemas import CreateChat, FullChat
from app.schemas.message_schemas import FullMessage, SendMessage, SendMessageResponse, RegenerateMessage, \
    RegenerateMessageResponse, MarkMessage, UpdateChatTitle
from app.schemas.user_schemas import FullUser

from app.services import get_chat_service, AuthService, ArticleService, get_article_service
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
    chat_uuid: Optional[UUID] = Form(None),
    parent_uuid: Optional[UUID] = Form(None),
    text: str = Form(...),
    files: list[UploadFile] = File(default=[]),
    user: FullUser = Depends(AuthService.get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    send_message_data = SendMessage(chat_uuid=chat_uuid, parent_uuid=parent_uuid, text=text)
    return await chat_service.send_message(send_message_data=send_message_data, files=files, owner_uuid=user.uuid)


@router.post("/regenerate_message", response_model=RegenerateMessageResponse)
async def send_message(
    regenerate_message_data: RegenerateMessage,
    user: FullUser = Depends(AuthService.get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
):
     return await chat_service.regenerate_message(regenerate_message_data=regenerate_message_data, owner_uuid=user.uuid)


@router.patch("/{chat_uuid}/title")
async def update_chat_title(
    chat_uuid: UUID,
    update_chat_title_data: UpdateChatTitle,
    user: FullUser = Depends(AuthService.get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    await chat_service.update_chat_title(chat_uuid=chat_uuid, new_title=update_chat_title_data.new_title)
    return {"status": "ok"}


@router.patch("/{message_uuid}/mark")
async def mark_message(
    message_uuid: UUID,
    mark_message_data: MarkMessage,
    user: FullUser = Depends(AuthService.get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    await chat_service.mark_message(message_uuid=message_uuid, mark=mark_message_data.mark)
    return {"status": "ok"}


@router.delete("/{chat_uuid}")
async def delete_chat(
    chat_uuid: UUID,
    user: FullUser = Depends(AuthService.get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    await chat_service.delete_chat(chat_uuid=chat_uuid, owner_uuid=user.uuid)
    return {"status": "ok"}


@router.websocket("/ws/{answer_uuid}")
async def websocket_endpoint(
    answer_uuid: UUID,
    websocket: WebSocket,
):
    await websocket.accept()
    await websocket.send_json({"type": "info", "message": "Connected"})

    async with resolve_async_generator(get_session()) as session:
        chat_service: ChatService = await get_chat_service(session=session)
        article_service: ArticleService = await get_article_service(session=session)
        messages = await chat_service.message_repository.get_message_history(message_uuid=answer_uuid)

        try:
            await websocket.send_json({"type": "start", "message": messages[-2]})

            last_user_message = messages[-2]
            context_from_article = await article_service.find_nearest_articles(text=last_user_message)

            history_prompt = ""
            for i, msg in enumerate(messages):
                if i == 0:
                    continue

                role = "Асистент" if i % 2 == 0 else "Користувач"
                history_prompt += f"{role}: {msg}\n"

            final_prompt = (
                f"Ознайомся з наступною інформацією з Кримінального Кодексу України, яка може буде корисна для "
                f"відповіді на питання:\n{context_from_article}\n\n{history_prompt}"
            )

            print(final_prompt)

            async with httpx.AsyncClient(timeout=300.0) as client:
                async with client.stream(
                    "POST",
                    "http://host.docker.internal:11434/api/generate",
                    json={
                        "model": "mistral",
                        "prompt": final_prompt,
                        "system": "Ти є юридичним асистентом. Завжди відповідай професійно та офіційно українською мовою. "
                                  "Якщо ти не знаєш чіткої відповіді на питання тоді просто вибчся і скажи, що ти цього не знаеш",
                        "stream": True
                    }
                ) as response:
                    accumulated = ""
                    async for line in response.aiter_lines():
                        if line:
                            data = json.loads(line)
                            token = data.get("response", "")
                            accumulated += token
                            await websocket.send_json({"type": "message", "message": accumulated})

            message = await chat_service.complete_answer(answer_uuid=answer_uuid, text=accumulated)
            await websocket.send_json({"type": "close", "message": jsonable_encoder(message)})

        except Exception as e:
            await websocket.send_json({"type": "error", "message": str(e)})
    await websocket.close()
