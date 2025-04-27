import requests
import structlog
from settings import Settings

logger = structlog.get_logger(__name__)
settings = Settings()
MINDSDB_API = settings.mindsdb_url.rstrip('/')

def create_gemini_model():
    sql = f"""
    CREATE MODEL IF NOT EXISTS google_gemini_model
    PREDICT answer
    USING
      engine = 'google_gemini_engine',
      column = 'question',
      model = 'gemini-pro';
    """
    try:
        r = requests.post(f"{MINDSDB_API}/sql/query", json={"query": sql})
        logger.info("Google Gemini model creation response", response=r.text)
        if r.status_code not in (200, 201, 409):
            logger.error("Failed to create Google Gemini model", details=r.text)
            return False
        logger.info("Google Gemini model created or already exists", name='google_gemini_model')
        return True
    except Exception as e:
        logger.error("Error creating Google Gemini model", error=str(e))
        return False
