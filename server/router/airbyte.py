from fastapi import APIRouter, HTTPException
from airbyte import list_destinations, list_sources, run_sync, setup_mongo_db_destination
from models import  SyncConfig, MongoDBConfig

airbyte_router = APIRouter(prefix="/airbyte", tags=["airbyte"])

@airbyte_router.get("/destinations", response_model=dict)
async def list_destinations_endpoint():
    """
    List all destinations in Airbyte.

    Args:
        credentials: TokenRequest object for authentication.

    Returns:
        dict: List of destinations.
    """
    try:
        return list_destinations()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@airbyte_router.get("/sources", response_model=dict)
async def list_sources_endpoint():
    """
    List all sources in Airbyte.

    Args:
        credentials: TokenRequest object for authentication.

    Returns:
        dict: List of sources.
    """
    try:
        return list_sources()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@airbyte_router.post("/destinations/mongodb", response_model=dict)
async def create_mongodb_destination(config: MongoDBConfig):
    """
    Create a MongoDB destination in Airbyte.

    Args:
        config: MongoDBConfig object containing workspaceId, cluster_url, database, username, and password.

    Returns:
        dict: Success message if the destination is created.
    """
    try:
        return setup_mongo_db_destination(config)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create MongoDB destination: {str(e)}")


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