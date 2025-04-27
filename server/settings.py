from pathlib import Path
import structlog
from pydantic_settings import BaseSettings
from pydantic import Field

logger = structlog.get_logger(__name__)

def create_path(folder_name: str) -> Path:
    """Creates and returns a path for storing data or logs."""
    path = Path(__file__).parent.resolve().parent / folder_name
    path.mkdir(exist_ok=True)
    return path

class Settings(BaseSettings):
    """
    Application settings model that provides configuration for all components.
    """
    port: int = Field(8080, env="PORT")

    # Airbyte
    airbyte_client_id: str = Field("", env="AIRBYTE_CLIENT_ID")
    airbyte_client_secret: str = Field("", env="AIRBYTE_CLIENT_SECRET")
    airbyte_workspace_id: str = Field("", env="AIRBYTE_WORKSPACE_ID")

    # MongoDB – Warehouse / Destination
    mongo_cluster_url: str = Field("", env="MONGO_CLUSTER_URL")
    mongo_database: str = Field("", env="MONGO_DATABASE")
    mongo_username: str = Field("", env="MONGO_USERNAME")
    mongo_password: str = Field("", env="MONGO_PASSWORD")

    # MindsDB
    mindsdb_url: str = Field("", env="MINDSDB_URL")

    # Gemini
    gemini_api_key: str = Field("", env="GEMINI_API_KEY")

    # Polygon
    polygon_api_key: str = Field("", env="POLYGON_API_KEY")
    polygon_start_date: str = Field("", env="POLYGON_START_DATE")

    # Slack
    slack_bot_token: str = Field("", env="SLACK_BOT_TOKEN")
    slack_bot_user_id: str = Field("", env="SLACK_BOT_USER_ID")
    slack_signing_secret: str = Field("", env="SLACK_SIGNING_SECRET")

    # Restrict backend listener to specific IPs
    cors_origins: list[str] = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
logger.debug("Settings have been initialized.", settings=settings.model_dump(exclude={"mongo_password"}))