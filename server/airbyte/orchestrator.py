import structlog
from .pipeline import list_sources, list_destinations, run_sync
from .sources import setup_shopify_source
from .destination import setup_mongo_db_destination
from settings import Settings
from mindsdb.connect import connect_to_mindsdb
import requests
from types import SimpleNamespace

logger = structlog.get_logger(__name__)
settings = Settings()

def setup_airbyte_connections():
    logger.info("Orchestrating Airbyte connections and sources...")
    # 1. Check for Shopify source
    sources = list_sources()
    shopify_source = None
    for src in sources.get("data", []):
        if src.get("sourceType", "").lower() == "shopify":
            shopify_source = src
            logger.info(f"Found Shopify source: {shopify_source.get('sourceId')}")
            break
    if not shopify_source:
        logger.info("Shopify source not found, creating...")
        setup_shopify_source({})
        sources = list_sources()  # Refresh
        shopify_source = next((src for src in sources.get("data", []) if src.get("sourceType", "").lower() == "shopify"), None)
        if shopify_source:
            logger.info(f"Created and found Shopify source: {shopify_source.get('sourceId')}")

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

    # 3. Find and run Shopify connections
    try:
        if shopify_source and mongo_dest:
            logger.info("Running Airbyte sync for Shopify → MongoDB...")
            # Enhanced error logging for sync
            try:
                logger.info(f"Sync details: sourceId={shopify_source.get('sourceId')}, destinationId={mongo_dest.get('destinationId')}")

                sync_config = SimpleNamespace(
                    sourceId=shopify_source.get("sourceId"),
                    destinationId=mongo_dest.get("destinationId")
                )
                run_sync(sync_config)
            except Exception as e:
                logger.error("Failed to run Airbyte sync", exc_info=True)
                return
        else:
            logger.warning("Shopify source or MongoDB destination missing, cannot run sync.")
    except Exception as e:
        logger.error("Failed to run Airbyte orchestration", exc_info=True)

    logger.info("Airbyte orchestration complete.")
