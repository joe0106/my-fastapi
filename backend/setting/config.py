import os
from functools import lru_cache
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


@lru_cache()
def get_settings():
    app_mode = os.getenv("APP_MODE", "dev")
    load_dotenv(BASE_DIR / f".env.{app_mode}")
    return Settings()

class Settings():
    def __init__(self):
        self.app_name: str = "iThome2023 FastAPI Tutorial"
        self.author: str = "Jason Liu"
        self.app_mode: str = os.getenv("APP_MODE", "dev")
        self.port: int = int(os.getenv("PORT", "8001"))
        self.reload: bool = _env_bool("RELOAD")
        self.db_type: str = os.getenv("DB_TYPE", "postgresql").upper()
        self.run_mode: str = os.getenv("RUN_MODE", "ASYNC").upper()
        self.database_url: str = os.getenv(f"{self.run_mode}_{self.db_type}_DATABASE_URL")
        self.access_token_secret: str = os.getenv("ACCESS_TOKEN_SECRET")
        self.access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1"))
        self.refresh_token_secret: str = os.getenv("REFRESH_TOKEN_SECRET")
        self.refresh_token_expire_minutes: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", "10"))
