import structlog
from .connect import connect_to_mindsdb

def setup_mindsdb_server():
    """
    Ensures the MindsDB server is reachable and active.
    Returns the base_url if available, otherwise raises an exception.
    """
    logger = structlog.get_logger(__name__)
    base_url = connect_to_mindsdb()
    logger.info("Using MindsDB URL", url=base_url)
    return base_url
