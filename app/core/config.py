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

    JWT_SECRET_KEY: str

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def SYNC_DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"


settings = Settings()
