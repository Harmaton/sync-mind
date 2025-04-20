import structlog
import requests
from settings import Settings
from fastapi import APIRouter, HTTPException

logger = structlog.get_logger(__name__)
settings = Settings()

MINDSDB_API = settings.mindsdb_url.rstrip('/')
PROJECT = "slack_project"
FORECAST_MODEL = "sales_forecast"
DATASOURCE = "shopify_mongo"
TABLE = "shopify_orders"  # Change if your collection name is different


def setup_forecast_model():
    """
    Creates a sales forecasting model in MindsDB if it doesn't exist.
    """
    sql = f"""
    CREATE MODEL {PROJECT}.{FORECAST_MODEL}
    PREDICT quantity
    USING
      engine = 'mongodb',
      datasource = '{DATASOURCE}',
      table = '{TABLE}',
      order_by = 'order_date',
      window = 10,
      horizon = 7;
    """
    # Try to create model directly via SQL endpoint
    r = requests.post(f"{MINDSDB_API}/api/sql/query", json={"query": sql})
    if r.status_code in (200, 201, 409):
        logger.info("Forecasting model created or already exists", name=FORECAST_MODEL)
        return True
    else:
        logger.error("Failed to create forecasting model", details=r.text)
        return False

forecast_router = APIRouter(prefix="/forecast", tags=["forecast"])

@forecast_router.post("/query")
def forecast_sales():
    sql = f"""
    SELECT quantity FROM {PROJECT}.{FORECAST_MODEL}
    WHERE order_date > NOW();
    """
    r = requests.post(f"{MINDSDB_API}/api/sql", json={"query": sql})
    if r.status_code == 200:
        return r.json()
    else:
        raise HTTPException(status_code=400, detail=r.text)
