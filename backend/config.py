from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/ofertas")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    ia_api_url: str = os.getenv("IA_API_URL", "https://api.tu-proveedor.com/v1/chat/completions")
    ia_api_key: str = os.getenv("IA_API_KEY", "tu-key")
    ia_model: str = os.getenv("IA_MODEL", "glm-5.1")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

config = Settings()