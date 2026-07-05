import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "EDUMITHRA -- AI Learning Copilot"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./edumithra.db")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "edumithra_super_secret_key_change_me_in_production_1234567890")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "")

    class Config:
        case_sensitive = True

settings = Settings()
