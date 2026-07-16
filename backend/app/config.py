from pydantic_settings import BaseSettings
from pydantic import ConfigDict
import os

# Resolve .env relative to this file's directory (backend/app/ → backend/.env)
_env_path = os.path.join(os.path.dirname(__file__), "../.env")

class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=_env_path,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Web Scraper Toolkit"
    request_timeout: float = 10.0
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ]

    # AI / Groq settings
    groq_api_key: str = ""
    ai_model: str = "llama-3.3-70b-versatile"
    ai_base_url: str = "https://api.groq.com/openai/v1"


settings = Settings()
