from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

app = FastAPI()

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