from pydantic import EmailStr
from pydantic_settings import BaseSettings

from dotenv import load_dotenv
load_dotenv()
class Settings(BaseSettings):
    DB_URL: str = "sqlite+aiosqlite:///./backend/fastpayqr.db"
    SECRET_KEY: str = "your-default-secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()


class MailSettings(BaseSettings):
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USE_TLS: bool = True
    SMTP_USE_SSL: bool = False
    MAIL_FROM: EmailStr

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


mail_settings = MailSettings()
