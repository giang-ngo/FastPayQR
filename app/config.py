import os
from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    DB_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./fastpayqr.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-default-secret")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7


settings = Settings()
