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

        # 1. Fetch all connections and log them for debugging
        list_url = "https://api.airbyte.com/v1/connections"
        list_headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        list_resp = requests.get(list_url, headers=list_headers)
        list_resp.raise_for_status()
        all_connections = list_resp.json().get("data", []) 

        # Try to find a connection with same sourceId and destinationId
        for c in all_connections:
            if c.get("sourceId") == config.sourceId and c.get("destinationId") == config.destinationId:
                logger.info("Found existing Airbyte connection")
                # If a sync is already running or recently triggered, do not trigger again
                if c.get("status") == "active":
                    logger.info("Sync already running or recently triggered; skipping new sync trigger.")
                    return {"existing_connection": c, "sync_skipped": True}
                # Otherwise, trigger a sync job for this connection
                job_url = "https://api.airbyte.com/v1/jobs"
                job_payload = {"connectionId": c["connectionId"], "jobType": "sync"}
                job_headers = {
                    "accept": "application/json",
                    "content-type": "application/json",
                    "Authorization": f"Bearer {access_token}"
                }
                job_resp = requests.post(job_url, json=job_payload, headers=job_headers)
                job_resp.raise_for_status()
                logger.info(f"Triggered sync job for existing connection: {job_resp.json()}")
                return {"existing_connection": c, "sync_job": job_resp.json()}

        # 2. If not found, create a new connection with cron schedule
        url = "https://api.airbyte.com/v1/connections"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        # Use the working cron expression 
        cron_expr = "0 0 * * * ?" 
        payload = {
            "sourceId": config.sourceId,
            "destinationId": config.destinationId,
            "name": "Polygon-Mongo Connection",
            "schedule": {
                "scheduleType": "cron",
                "cronExpression": cron_expr
            },
            "namespaceDefinition": "destination",
            "nonBreakingSchemaUpdatesBehavior": "ignore"
        }
        logger.info(f"Creating Airbyte connection with payload: {payload}")
        response = requests.post(url, json=payload, headers=headers)
        try:
            response.raise_for_status()
        except Exception as e:
            logger.error("Airbyte connection creation failed", status_code=response.status_code, response=response.text)
            raise
        logger.info(f"Airbyte connection creation response: {response.text}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Error running sync", error=str(e), response=getattr(e.response, 'text', None))
        raise ValueError(f"Failed to run sync: {str(e)}")