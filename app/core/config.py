from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str | None = None
    MYSQL_URL: str | None = None
    APP_NAME: str = "CartAPI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    LOG_TO_FILE: bool = False

    @property
    def database_url(self) -> str:
        url = self.DATABASE_URL or self.MYSQL_URL
        if not url:
            raise ValueError("DATABASE_URL or MYSQL_URL must be set")
        return url

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()