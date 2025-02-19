from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routes import helthcheck_route
from app.routes import auth_route
app = FastAPI()

app.include_router(router=helthcheck_route.router, tags=["healthcheck"])
app.include_router(router=auth_route.router, tags=["auth"])

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