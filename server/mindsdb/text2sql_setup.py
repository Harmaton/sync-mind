import structlog
import requests
from settings import Settings

logger = structlog.get_logger(__name__)
settings = Settings()

MINDSDB_API = settings.mindsdb_url.rstrip('/')
PROJECT = "slack_project"
DATASOURCE = "shopify_mongo"
TABLES = ["shopify_orders"]  # Replace with your actual MongoDB collection(s)

def setup_text2sql_skill():
    sql = f"""
    CREATE SKILL {PROJECT}.shopify_text2sql
    TYPE 'text2sql'
    USING DATABASE = '{DATASOURCE}', TABLES = {TABLES}, DESCRIPTION = 'Text-to-SQL skill for querying Shopify data in MongoDB.';
    """
    logger.info("Creating Text2SQL skill using SQL query", query=sql)
    r = requests.post(f"{MINDSDB_API}/api/sql/query", json={"query": sql})
    if r.status_code in (200, 201, 409):
        logger.info("Text2SQL skill added or already exists", name="shopify_text2sql")
        return True
    else:
        logger.error("Failed to add Text2SQL skill", details=r.text)
        return False

# Endpoint for querying Text2SQL skill
from fastapi import APIRouter, HTTPException
text2sql_router = APIRouter(prefix="/text2sql", tags=["text2sql"])

@text2sql_router.post("/query")
def query_text2sql(question: str):
    try:
        payload = {"question": question}
        r = requests.post(f"{MINDSDB_API}/api/projects/{PROJECT}/skills/shopify_text2sql/completions", json=payload)
        if r.status_code == 200:
            return r.json()
        else:
            logger.error("Text2SQL query failed", details=r.text)
            raise HTTPException(status_code=400, detail=r.text)
    except Exception as e:
        logger.error("Text2SQL query error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
