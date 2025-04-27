import structlog
from .pipeline import list_sources, list_destinations, run_sync
from .sources import setup_SPX_polygon_source
from .destination import setup_mongo_db_destination
from settings import Settings
from types import SimpleNamespace

logger = structlog.get_logger(__name__)
settings = Settings()

def setup_airbyte_connections():
    logger.info("Orchestrating Airbyte connections and sources...")
    # 1. Check for Polygon source
    sources = list_sources()
    polygon_source = None
    for src in sources.get("data", []):
        if src.get("sourceType", "").lower() == "polygon-stock-api":
            polygon_source = src
            logger.info(f"Found Polygon source: {polygon_source.get('sourceId')}")
            break
    if not polygon_source:
        logger.info("Polygon source not found, creating...")
        setup_SPX_polygon_source({})
        sources = list_sources()  # Refresh
        polygon_source = next((src for src in sources.get("data", []) if src.get("sourceType", "").lower() == "polygon-stock-api"), None)
        if polygon_source:
            logger.info(f"Created and found Polygon source: {polygon_source.get('sourceId')}")

    # 2. Check for MongoDB destination
    destinations = list_destinations()
    mongo_dest = None
    for dest in destinations.get("data", []):
        if dest.get("destinationType", "").lower() == "mongodb":
            mongo_dest = dest
            logger.info(f"Found MongoDB destination: {mongo_dest.get('destinationId')}")
            break
    if not mongo_dest:
        logger.info("MongoDB destination not found, creating...")
        setup_mongo_db_destination()
        destinations = list_destinations()  # Refresh
        mongo_dest = next((dest for dest in destinations.get("data", []) if dest.get("destinationType", "").lower() == "mongodb"), None)
        if mongo_dest:
            logger.info(f"Created and found MongoDB destination: {mongo_dest.get('destinationId')}")

    # 3. Find and run Polygon connections
    try:
        if polygon_source and mongo_dest:
            logger.info("Running Airbyte sync for Polygon → MongoDB...")
            # Enhanced error logging for sync
            try:
                logger.info(f"Sync details: sourceId={polygon_source.get('sourceId')}, destinationId={mongo_dest.get('destinationId')}")

                sync_config = SimpleNamespace(
                    sourceId=polygon_source.get("sourceId"),
                    destinationId=mongo_dest.get("destinationId")
                )
                run_sync(sync_config)
            except Exception as e:
                logger.error("Failed to run Airbyte sync", exc_info=True)
                return
        else:
            logger.warning("Polygon source or MongoDB destination missing, cannot run sync.")
    except Exception as e:
        logger.error("Failed to run Airbyte orchestration", exc_info=True)

    logger.info("Airbyte orchestration complete.")
