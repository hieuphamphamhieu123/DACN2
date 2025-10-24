from pydantic_settings import BaseSettings
import os
from pathlib import Path

class Settings(BaseSettings):
    mongodb_url: str
    database_name: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = os.path.join(Path(__file__).parent.parent, ".env")
        env_file_encoding = 'utf-8'

settings = Settings()