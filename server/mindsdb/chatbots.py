import requests
import structlog
from settings import Settings

logger = structlog.get_logger(__name__)
settings = Settings()
MINDSDB_API = settings.mindsdb_url.rstrip('/')

def create_advisor_chatbot():
    sql = f"""
    CREATE CHATBOT IF NOT EXISTS advisor_chatbot
    USING
      database   = 'slack',
      agent      = 'advisor_agent',
      is_running = true;
    """
    try:
        r = requests.post(f"{MINDSDB_API}/sql/query", json={"query": sql})
        logger.info("Slack chatbot creation response", response=r.text)
        if r.status_code not in (200, 201, 409):
            logger.error("Failed to create Slack chatbot", details=r.text)
            return False
        logger.info("Slack chatbot created or already exists", name='slack_chatbot')
        return True
    except Exception as e:
        logger.error("Error creating Slack chatbot", error=str(e))
        return False
