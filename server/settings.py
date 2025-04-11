from pathlib import Path

import structlog
from pydantic_settings import BaseSettings

logger = structlog.get_logger(__name__)


def create_path(folder_name: str) -> Path:
    """Creates and returns a path for storing data or logs."""
    path = Path(__file__).parent.resolve().parent / f"{folder_name}"
    path.mkdir(exist_ok=True)
    return path


class Settings(BaseSettings):
    """
    Application settings model that provides configuration for all components.
    Combines both infrastructure and consensus settings.
    """

 
    # Gemini Settings
    gemini_api_key: str = ""

    # Restrict backend listener to specific IPs
    cors_origins: list[str] = ["*"]
  

# Create a global settings instance
settings = Settings()
logger.debug("Settings have been initialized.", settings=settings.model_dump())
logger.debug(
    "settings",
    settings=settings.model_dump(
        exclude={"x_api_key_secret", "x_access_token_secret", "telegram_api_token"}
    ),)
