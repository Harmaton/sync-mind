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

def create_forecast_model():
    sql = f"""
    CREATE MODEL IF NOT EXISTS price_forecast_model
    FROM stocks_db
    (SELECT * FROM price)
    PREDICT price
    ORDER BY day
    WINDOW 12
    HORIZON 3
    USING ENGINE = 'forecast_engine';
    """
    try:
        r = requests.post(f"{MINDSDB_API}/sql/query", json={"query": sql})
        logger.info("Performance forecasting model creation response", response=r.text)
        if r.status_code not in (200, 201, 409):
            logger.error("Failed to create performance forecasting model", details=r.text)
            return False
        logger.info("Performance forecasting model created or already exists", name='performance_forecast')
        return True
    except Exception as e:
        logger.error("Error creating performance forecasting model", error=str(e))
        return False

def create_langchain_model():
    sql = f"""
    CREATE MODEL langchain_openai_model
    PREDICT completion
    USING
        engine = 'langchain_engine',      
        provider = 'openai',               
        openai_api_key = '{settings.openai_api_key}',  
        model_name = 'gpt-4',      
        mode = 'conversational',           -- conversational mode
        user_column = 'question',          -- column name that stores input from the user
        assistant_column = 'completion',       -- column name that stores output of the model (see PREDICT column)
        verbose = True,
        prompt_template = 'You are a helpful trading financial advisor who can answer questions about stocks, bonds, and other financial instruments: {{question}}',
        max_tokens = 4096;
    """
    try:
        r = requests.post(f"{MINDSDB_API}/sql/query", json={"query": sql})
        logger.info("Langchain model creation response", response=r.text)
        if r.status_code not in (200, 201, 409):
            logger.error("Failed to create Langchain model", details=r.text)
            return False
        logger.info("Langchain model created or already exists", name='langchain_model')
        return True
    except Exception as e:
        logger.error("Error creating Langchain model", error=str(e))
        return False