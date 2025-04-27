import requests
import structlog
from settings import Settings

logger = structlog.get_logger(__name__)
settings = Settings()
MINDSDB_API = settings.mindsdb_url.rstrip('/')

def create_advisor_agent():
    sql = f"""
    CREATE AGENT advisor_agent
    WITH
      model = 'google_gemini_model',
      skills = ['stocks_text2sql_skill'];
    """
    try:
        r = requests.post(f"{MINDSDB_API}/sql/query", json={"query": sql})
        logger.info("Slack agent creation response", response=r.text)
        if r.status_code not in (200, 201, 409):
            logger.error("Failed to create Slack agent", details=r.text)
            return False
        logger.info("Slack agent created or already exists", name='slack_agent')
        return True
    except Exception as e:
        logger.error("Error creating Slack agent", error=str(e))
        return False
