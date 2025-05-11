from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routes import helthcheck_route
from app.routes import auth_route
from app.routes import article_route
from app.routes import chat_route
app = FastAPI()

app.include_router(router=helthcheck_route.router, tags=["Healthcheck"])
app.include_router(router=auth_route.router, tags=["Auth"], prefix="/auth")
app.include_router(router=article_route.router, tags=["Article"], prefix="/article")
app.include_router(router=chat_route.router, tags=["Chat"], prefix="/chats")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    from uvicorn import run as uvicorn_run

    uvicorn_run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.PORT)