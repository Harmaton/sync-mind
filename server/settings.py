from pathlib import Path
import structlog
from pydantic_settings import BaseSettings
from pydantic import Field

logger = structlog.get_logger(__name__)

def create_path(folder_name: str) -> Path:
    """Creates and returns a path for storing data or logs."""
    path = Path(__file__).parent.resolve().parent / f"{folder_name}"
    path.mkdir(exist_ok=True)
    return path

class Settings(BaseSettings):
    """
    Application settings model that provides configuration for all components.
    """
    port: int = 8080
    # Airbyte Settings
    airbyte_client_id: str = ""
    airbyte_client_secret: str = ""
    airbyte_workspace_id: str = ""

    #shopify
    shopify_api_password: str =""
    shopify_shop: str=""
    
    # MongoDB Settings
    mongo_cluster_url: str = ""
    mongo_database: str = ""
    mongo_username: str = ""
    mongo_password: str = ""
    
    # MindsDB Settings
    mindsdb_url: str = ""

    # Gemini
    gemini_api_key: str = ""
    
    # Slack Settings
    slack_client_id: str = ""
    slack_client_secret: str = ""
    slack_signing_secret: str = ""
    slack_redirect_uri: str = ""
    slack_channel_id: str = ""
    slack_bot_token: str = Field(default="", env="SLACK_BOT_TOKEN")
    slack_bot_user_id: str = Field(default="", env="SLACK_BOT_USER_ID")
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    
    # Restrict backend listener to specific IPs
    cors_origins: list[str] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create a global settings instance
settings = Settings()
logger.debug("Settings have been initialized.")
logger.debug(
    "settings",
    settings=settings.model_dump(
        exclude={"airbyte_client_secret", "slack_client_secret", "slack_signing_secret", "mongo_password"}
    ),
)