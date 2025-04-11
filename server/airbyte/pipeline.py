import os
import requests
import structlog
from models import  TokenRequest, SyncConfig, MotherDuckConfigRequest, CoinAPIConfig

logger = structlog.get_logger(__name__)


def generate_token(credentials: TokenRequest) -> dict:
    """
    Generate an Airbyte API token using client credentials.

    Args:
        credentials: TokenRequest object with client_id, client_secret, and optional grant_type.

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
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "grant_type": credentials.grant_type
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

def list_destinations(credentials: TokenRequest) -> dict:
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
        token_response = generate_token(credentials)
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

def list_sources(credentials: TokenRequest) -> dict:
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
        token_response = generate_token(credentials)
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

def config_destination_mduck(config: MotherDuckConfigRequest) -> dict:
    """
    Configure a MotherDuck destination in Airbyte.

    Args:
        config: MotherDuckConfigRequest with workspaceId, motherduck_api_key, destination_path, schema.

    Returns:
        dict: Configured destination details.

    Raises:
        ValueError: For authentication or API errors.
    """
    try:
        token_response = generate_token(TokenRequest(
            client_id=os.getenv("AIRBYTE_CLIENT_ID", ""),
            client_secret=os.getenv("AIRBYTE_SECRET_ACCESS", "")
        ))
        access_token = token_response.get("access_token")
        if not access_token:
            raise ValueError("Failed to obtain access token")

        url = "https://api.airbyte.com/v1/destinations"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        payload = {
            "name": "destination-MotherDuck",
            "workspaceId": config.workspaceId,
            "configuration": {
                "destinationType": "duckdb",
                "motherduck_api_key": config.motherduck_api_key,
                "destination_path": f"md:{config.destination_path}",
                "schema": config.schema
            }
        }

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Error configuring MotherDuck destination", error=str(e))
        raise ValueError(f"Failed to configure destination: {str(e)}")

def config_source_coinapi(config: CoinAPIConfig) -> dict:
    """
    Configure a CoinAPI source in Airbyte.

    Args:
        config: CoinAPIConfig with api_key and symbol_id.

    Returns:
        dict: Configured source details.

    Raises:
        ValueError: For authentication or API errors.
    """
    try:
        token_response = generate_token(TokenRequest(
            client_id=os.getenv("AIRBYTE_CLIENT_ID", ""),
            client_secret=os.getenv("AIRBYTE_SECRET_ACCESS", "")
        ))
        access_token = token_response.get("access_token")
        if not access_token:
            raise ValueError("Failed to obtain access token")

        url = "https://api.airbyte.com/v1/sources"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        payload = {
            "api_key": config.api_key,
            "configuration": {"sourceType": "coin-api"},
            "start_date": "2019-01-01T00:00:00",
            "symbol_id": config.symbol_id,
            "environment": os.getenv("COIN_ENVIRONMENT", "")
        }

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Error configuring CoinAPI source", error=str(e))
        raise ValueError(f"Failed to configure source: {str(e)}")

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
        token_response = generate_token(TokenRequest(
            client_id=os.getenv("AIRBYTE_CLIENT_ID", ""),
            client_secret=os.getenv("AIRBYTE_SECRET_ACCESS", "")
        ))
        access_token = token_response.get("access_token")
        if not access_token:
            raise ValueError("Failed to obtain access token")

        url = "https://api.airbyte.com/v1/connections"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        payload = {
            "sourceId": config.sourceId,
            "destinationId": config.destinationId,
            "schedule": {
                "scheduleType": "cron",
                "cronExpression": "0 0 * * * ?"
            }
        }

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Error running sync", error=str(e))
        raise ValueError(f"Failed to run sync: {str(e)}")