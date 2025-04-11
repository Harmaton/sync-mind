from fastapi import APIRouter, HTTPException
from airbyte import (
list_destinations, list_sources,
config_destination_mduck,
config_source_coinapi, run_sync
)
from models import TokenRequest, MotherDuckConfigRequest, CoinAPIConfig, SyncConfig

airbyte_router = APIRouter(prefix="/airbyte", tags=["airbyte"])

@airbyte_router.post("/destinations", response_model=dict)
async def list_destinations_endpoint(credentials: TokenRequest):
    """
    List all destinations in Airbyte.

    Args:
        credentials: TokenRequest object for authentication.

    Returns:
        dict: List of destinations.
    """
    try:
        return list_destinations(credentials)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@airbyte_router.post("/sources", response_model=dict)
async def list_sources_endpoint(credentials: TokenRequest):
    """
    List all sources in Airbyte.

    Args:
        credentials: TokenRequest object for authentication.

    Returns:
        dict: List of sources.
    """
    try:
        return list_sources(credentials)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@airbyte_router.post("/configure-destination-mduck", response_model=dict)
async def config_destination_mduck_endpoint(config: MotherDuckConfigRequest):
    """
    Configure a MotherDuck destination in Airbyte.

    Args:
        config: MotherDuckConfigRequest with workspaceId, motherduck_api_key, destination_path, schema.

    Returns:
        dict: Configured destination details.
    """
    try:
        return config_destination_mduck(config)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@airbyte_router.post("/configure-source-coinapi", response_model=dict)
async def config_source_coinapi_endpoint(config: CoinAPIConfig):
    """
    Configure a CoinAPI source in Airbyte.

    Args:
        config: CoinAPIConfig with api_key and symbol_id.

    Returns:
        dict: Configured source details.
    """
    try:
        return config_source_coinapi(config)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@airbyte_router.post("/run-sync", response_model=dict)
async def run_sync_endpoint(config: SyncConfig):
    """
    Configure and run a sync connection in Airbyte.

    Args:
        config: SyncConfig with sourceId and destinationId.

    Returns:
        dict: Sync connection details.
    """
    try:
        return run_sync(config)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))