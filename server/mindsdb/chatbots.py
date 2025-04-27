import requests
import structlog
from settings import Settings

logger = structlog.get_logger(__name__)
settings = Settings()
MINDSDB_API = settings.mindsdb_url.rstrip('/')
DEFAULT_DATASOURCE = "stocks_db"

def create_advisor_chatbot():
    sql = f"""
    CREATE CHATBOT advisor_chatbot
    USING
      database   = '{DEFAULT_DATASOURCE}',
      agent      = 'advisor_agent',
      is_running = true;
    """
    try:
        r = requests.post(f"{MINDSDB_API}/sql/query", json={"query": sql})
        logger.info("Stocks chatbot creation response", response=r.text)
        if r.status_code not in (200, 201, 409):
            logger.error("Failed to create Stocks chatbot", details=r.text)
            return False
        logger.info("Stocks chatbot created or already exists", name='stocks_chatbot')
        return True
    except Exception as e:
        logger.error("Error creating Stocks chatbot", error=str(e))
        return False
