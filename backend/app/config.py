from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./livemart.db"
    
    # JWT
    SECRET_KEY: str = "14feb88b397106808906b5a987c5ab73b34a4414e79cb31a962bcec4759b1f7b"  # Change this in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Email settings
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = "LiveMart"
    SMTP_PASSWORD: str = "niojhfpbvngfewva"
    EMAIL_FROM: str = "livemart25@gmail.com"
    
    # OTP settings
    OTP_LENGTH: int = 6
    OTP_EXPIRE_MINUTES: int = 15

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()