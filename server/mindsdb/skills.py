import requests
import structlog
from settings import Settings

logger = structlog.get_logger(__name__)
settings = Settings()
MINDSDB_API = settings.mindsdb_url.rstrip('/')
DEFAULT_DATASOURCE = "stocks_db"

def create_stocks_text2sql_skill():
    sql = f"""
    CREATE SKILL stocks_text2sql_skill
    USING
      type      = 'text2sql',
      database    = '{DEFAULT_DATASOURCE}',
      tables      = ['stocks'],
      description = 'Stocks data';
    """
    try:
        r = requests.post(f"{MINDSDB_API}/sql/query", json={"query": sql})
        logger.info("Stocks Text2SQL skill creation response", response=r.text)
        if r.status_code not in (200, 201, 409):
            logger.error("Failed to create Shopify Text2SQL skill", details=r.text)
            return False
        logger.info("Shopify Text2SQL skill created or already exists", name='shopify_text2sql_skill')
        return True
    except Exception as e:
        logger.error("Error creating Shopify Text2SQL skill", error=str(e))
        return False
