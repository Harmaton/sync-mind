import requests
import structlog
from settings import Settings

logger = structlog.get_logger(__name__)
settings = Settings()
MINDSDB_API = settings.mindsdb_url.rstrip('/')

def create_google_gemini_engine():
    sql = f"""
    CREATE ML_ENGINE IF NOT EXISTS google_gemini_engine
    FROM google_gemini
    USING
      api_key = '{settings.gemini_api_key}';
    """
    try:
        r = requests.post(f"{MINDSDB_API}/sql/query", json={"query": sql})
        logger.info("Google Gemini engine creation response", response=r.text)
        if r.status_code not in (200, 201, 409):
            logger.error("Failed to create Google Gemini engine", details=r.text)
            return False
        logger.info("Google Gemini engine created or already exists", name='google_gemini_engine')
        return True
    except Exception as e:
        logger.error("Error creating Google Gemini engine", error=str(e))
        return False
