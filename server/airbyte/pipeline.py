import requests
import structlog
from models import  SyncConfig
from settings import Settings

logger = structlog.get_logger(__name__)
settings = Settings()

def generate_token() -> dict:
    """
    Generate an Airbyte API token using client credentials.
    Returns:
        dict: Token response containing access_token.

    Raises:
        ValueError: For specific error statuses (400, 403, 404).
    """
    url = "https://api.airbyte.com/v1/applications/token"
    headers = {
        "Content-Type": "application/json",
        "accept": "application/json"
    }
    payload = {
        "client_id": settings.airbyte_client_id,
        "client_secret": settings.airbyte_client_secret,
        "grant_type": "client_credentials"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Airbyte token generation failed", error=str(e), status=response.status_code if 'response' in locals() else None)
        if 'response' in locals():
            if response.status_code == 404:
                raise ValueError("Invalid Airbyte API endpoint")
            elif response.status_code == 400:
                raise ValueError("Invalid credentials format")
            elif response.status_code == 403:
                raise ValueError("Invalid credentials or unauthorized")
        raise ValueError(f"Token generation failed: {str(e)}")

def list_destinations() -> dict:
    """
    List all destinations in Airbyte.

    Args:
        credentials: TokenRequest object for authentication.

    Returns:
        dict: List of destinations.

    Raises:
        ValueError: For authentication or API errors.
    """
    try:
        token_response = generate_token()
        access_token = token_response.get("access_token")
        if not access_token:
            raise ValueError("Failed to obtain access token")

        url = "https://api.airbyte.com/v1/destinations"
        headers = {
            "Content-Type": "application/json",
            "accept": "application/json",
            "Authorization": f"Bearer {access_token}"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Airbyte API error", error=str(e), status=response.status_code if 'response' in locals() else None)
        if 'response' in locals() and response.status_code == 401:
            raise ValueError("Authentication failed - invalid token")
        raise ValueError(f"Failed to list destinations: {str(e)}")

def list_sources() -> dict:
    """
    List all sources in Airbyte.

    Args:
        credentials: TokenRequest object for authentication.

    Returns:
        dict: List of sources.

    Raises:
        ValueError: For authentication or API errors.
    """
    try:
        token_response = generate_token()
        access_token = token_response.get("access_token")
        if not access_token:
            raise ValueError("Failed to obtain access token")

        url = "https://api.airbyte.com/v1/sources"
        headers = {
            "Content-Type": "application/json",
            "accept": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Airbyte API error", error=str(e), status=response.status_code if 'response' in locals() else None)
        if 'response' in locals() and response.status_code == 401:
            raise ValueError("Authentication failed - invalid token")
        raise ValueError(f"Failed to list sources: {str(e)}")

def run_sync(config: SyncConfig) -> dict:
    """
    Configure and run a sync connection in Airbyte.

    Args:
        config: SyncConfig with sourceId and destinationId.

    Returns:
        dict: Sync connection details.

    Raises:
        ValueError: For authentication or API errors.
    """
    try:
        token_response = generate_token()
        access_token = token_response.get("access_token")
        if not access_token:
            raise ValueError("Failed to obtain access token")

        url = "https://api.airbyte.com/v1/connections"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        # Use default connection settings as per Airbyte docs
        payload = {
            "sourceId": config.sourceId,
            "destinationId": config.destinationId,
            "schedule": {
                "scheduleType": "cron",
                "cronExpression": "0 0 * * * ?"
            }
        }
        # Remove keys with None values
        payload = {k: v for k, v in payload.items() if v is not None}

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Error running sync", error=str(e), response=getattr(e.response, 'text', None))
        raise ValueError(f"Failed to run sync: {str(e)}")