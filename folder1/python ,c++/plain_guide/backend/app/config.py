from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    app_name: str = "SKYGUARD AI"
    database_url: str = f"sqlite:///{BASE_DIR / 'skyguard.db'}"
    debug: bool = True
    websocket_broadcast_interval: float = 1.0

    class Config:
        env_file = BASE_DIR / ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
