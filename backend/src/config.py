from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API Keys
    openai_api_key: Optional[str] = None
    qdrant_api_key: Optional[str] = None

    # Database
    neon_database_url: Optional[str] = None

    # Qdrant Configuration
    qdrant_host: Optional[str] = "localhost"
    qdrant_port: int = 6333

    # Authentication
    jwt_secret: Optional[str] = "your-default-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Application
    environment: str = "development"
    debug: bool = True
    log_level: str = "info"

    # Vercel
    vercel_token: Optional[str] = None

    # AI Configuration
    openai_model: str = "gpt-4-turbo"
    embedding_model: str = "text-embedding-3-small"

    class Config:
        env_file = ".env"


settings = Settings()