from pydantic_settings import BaseSettings
from typing import Optional
from pydantic import ConfigDict, Field
from dotenv import load_dotenv
import os

# Load environment variables from .env file before creating Settings
load_dotenv()

class Settings(BaseSettings):
    # Cohere Configuration
    cohere_api_key: Optional[str] = Field(default=None, env="COHERE_API_KEY")

    # Google Gemini Configuration
    gemini_api_key: Optional[str] = Field(default=None, env="GEMINI_API_KEY")

    # Qdrant Configuration
    qdrant_api_key: Optional[str] = Field(default=None, env="QDRANT_API_KEY")
    qdrant_host: str = Field(default="localhost", env="QDRANT_HOST")
    qdrant_port: int = Field(default=6333, env="QDRANT_PORT")

    # Book Configuration
    book_url: Optional[str] = Field(default=None, env="BOOK_URL")

    # Processing Configuration
    chunk_size: int = Field(default=800, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=100, env="CHUNK_OVERLAP")
    max_pages: int = Field(default=1000, env="MAX_PAGES")
    rate_limit_delay: float = Field(default=1.0, env="RATE_LIMIT_DELAY")

    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    # Collection name for Qdrant
    collection_name: str = "textbook_content"

    # Textbook RAG Configuration
    textbook_mode_enabled: bool = Field(default=True, env="TEXTBOOK_MODE_ENABLED")
    max_history_turns: int = Field(default=10, env="MAX_HISTORY_TURNS")
    session_ttl_hours: int = Field(default=24, env="SESSION_TTL_HOURS")
    academic_tone_enforcement: bool = Field(default=True, env="ACADEMIC_TONE_ENFORCEMENT")
    reference_required: bool = Field(default=True, env="REFERENCE_REQUIRED")
    polite_language_handling: bool = Field(default=True, env="POLITE_LANGUAGE_HANDLING")
    max_response_length: int = Field(default=2000, env="MAX_RESPONSE_LENGTH")
    fallback_message: str = Field(
        default="The requested information is not available in the current knowledge base.",
        env="FALLBACK_MESSAGE"
    )

    model_config = ConfigDict(
        env_file_encoding="utf-8",
        case_sensitive=False,  # Use case-insensitive matching
        extra="ignore"  # Ignore extra fields
    )

# Global settings instance - load after environment is set
settings = Settings()

def validate_settings():
    """
    Validate that required settings are present
    """
    errors = []

    if not settings.cohere_api_key:
        errors.append("WARNING: COHERE_API_KEY not set — embedding service will fail")

    if not settings.qdrant_api_key:
        errors.append("WARNING: QDRANT_API_KEY not set — vector search will fail")

    if not settings.qdrant_host or settings.qdrant_host == "localhost":
        errors.append("WARNING: QDRANT_HOST not set or is localhost — vector search may fail in production")

    if settings.chunk_size <= 0:
        errors.append("CHUNK_SIZE must be positive")

    if settings.chunk_overlap < 0:
        errors.append("CHUNK_OVERLAP cannot be negative")

    if settings.max_pages <= 0:
        errors.append("MAX_PAGES must be positive")

    if settings.rate_limit_delay < 0:
        errors.append("RATE_LIMIT_DELAY cannot be negative")

    return errors

if __name__ == "__main__":
    # Test configuration loading
    print("Configuration loaded:")
    print(f"  Cohere API Key: {'SET' if settings.cohere_api_key else 'NOT SET'}")
    print(f"  Qdrant Host: {settings.qdrant_host}")
    print(f"  Qdrant Port: {settings.qdrant_port}")
    print(f"  Book URL: {settings.book_url}")
    print(f"  Chunk Size: {settings.chunk_size}")
    print(f"  Chunk Overlap: {settings.chunk_overlap}")
    print(f"  Textbook Mode Enabled: {settings.textbook_mode_enabled}")
    print(f"  Max History Turns: {settings.max_history_turns}")
    print(f"  Academic Tone Enforcement: {settings.academic_tone_enforcement}")
    print(f"  Reference Required: {settings.reference_required}")

    errors = validate_settings()
    if errors:
        print("\nConfiguration errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("\nAll configuration is valid!")