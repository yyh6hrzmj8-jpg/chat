from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "Chat Support Bot"
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./app.db")

    JWT_SECRET_KEY: str = Field(default="CHANGE_ME_PLEASE")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    CORS_ALLOW_ORIGINS: List[str] = Field(default_factory=lambda: ["http://localhost:5173", "http://localhost:5500", "http://127.0.0.1:5500", "http://localhost:8000", "*"])

settings = Settings()
