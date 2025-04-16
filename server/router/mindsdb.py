import structlog
from fastapi import APIRouter, HTTPException, Depends
from mindsdb import connect_to_mindsdb, list_datasources, create_postgres_datasource
from models import PostgresDataSourceCreate, MindsDBPingResponse
from mindsdb import query_ten

logger = structlog.get_logger(__name__)

# Create router
mindsdb_router = APIRouter(prefix="/mindsdb", tags=["mindsdb"])

# Dependency to get MindsDB connection service
def get_mindsdb_service():
    """Dependency to get MindsDB connection service"""
    try:
        service = connect_to_mindsdb()
        return service
    except Exception as e:
        logger.error(f"Failed to connect to MindsDB: {str(e)}")
        raise HTTPException(
            status_code=503, 
            detail="MindsDB service unavailable"
        )

@mindsdb_router.get("/query")
async def query():
    try:
        return query_ten()
    except Exception as e:
        logger.error(f"error")

@mindsdb_router.get("/ping", response_model=MindsDBPingResponse)
async def ping_mindsdb(
    mindsdb_service = Depends(get_mindsdb_service)
):
    """Check if MindsDB is reachable"""
    try:
        return {"status": "connected", "message": "MindsDB is reachable"}
    except Exception as e:
        logger.error(f"MindsDB ping failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"MindsDB connection failed: {str(e)}"
        )

@mindsdb_router.get("/datasources")
async def get_all_datasources(
    mindsdb_service = Depends(get_mindsdb_service)
):
    """List all available datasources from MindsDB"""
    try:
        datasources = list_datasources(mindsdb_service)
        if not datasources:
            return {"message": "No datasources found"}
        return {"datasources": datasources}
    except Exception as e:
        logger.error(f"Error fetching datasources: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve datasources: {str(e)}"
        )

@mindsdb_router.get("/datasources/{datasource_name}")
async def get_datasource(
    datasource_name: str,
    mindsdb_service = Depends(get_mindsdb_service)
):
    """Get information about a specific datasource"""
    try:
        datasources = list_datasources(mindsdb_service)
        # Assuming datasources is a list of names or a list of dicts with 'name' field
        if isinstance(datasources[0], dict):
            datasource_names = [d.get('name') for d in datasources]
        else:
            datasource_names = datasources
            
        if datasource_name not in datasource_names:
            return {"message": f"Datasource '{datasource_name}' not found"}
        
        # Return more detailed info if available
        for source in datasources:
            if isinstance(source, dict) and source.get('name') == datasource_name:
                return {"datasource": source}
        
        return {"datasource": datasource_name}
    except Exception as e:
        logger.error(f"Error fetching datasource {datasource_name}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve datasource: {str(e)}"
        )

