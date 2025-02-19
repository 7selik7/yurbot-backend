from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    HOST: str
    LOCAL_PORT: int
    PORT: int
    RELOAD: bool

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_LOCAL_PORT: int
    DB_NAME: str

    REDIS_DOMAIN: str
    REDIS_PORT: int
    REDIS_LOCAL_PORT: int

    class Config:
        env_file = ".env"


settings = Settings()