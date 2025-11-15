from pydantic_settings import BaseSettings
import os
from pathlib import Path
from typing import Optional

class Settings(BaseSettings):
    # JWT Settings
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Legacy MongoDB settings (not used anymore - using Firebase Firestore)
    mongodb_url: Optional[str] = None
    database_name: Optional[str] = None

    class Config:
        env_file = os.path.join(Path(__file__).parent.parent, ".env")
        env_file_encoding = 'utf-8'

settings = Settings()