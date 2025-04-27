import requests
import structlog
from settings import Settings

logger = structlog.get_logger(__name__)
settings = Settings()
MINDSDB_API = settings.mindsdb_url.rstrip('/')
DEFAULT_DATASOURCE = "stocks_db"

def create_slack_datasource_in_mindsdb():
    sql = f"""
    CREATE DATABASE IF NOT EXISTS slack_datasource
    WITH
      ENGINE = 'slack',
      PARAMETERS = {{
          "token": "{settings.slack_bot_token}"
        }};
    """
    try:
        r = requests.post(f"{MINDSDB_API}/sql/query", json={"query": sql})
        logger.info("Slack datasource creation response", response=r.text)
        if r.status_code in (200, 201, 409):
            logger.info("Slack datasource created or already exists", name='slack_datasource')
            return True
        else:
            logger.error("Failed to create Slack datasource", details=r.text)
            return False
    except Exception as e:
        logger.error("Error creating Slack datasource", error=str(e))
        return False

def create_mongo_datasource():
    url = f"{MINDSDB_API}/sql/query"
    sql = f'''
    CREATE DATABASE IF NOT EXISTS {DEFAULT_DATASOURCE}
    WITH
    ENGINE = 'mongodb',
    PARAMETERS = {{
        "host": "mongodb+srv://{settings.mongo_username}:{settings.mongo_password}@{settings.mongo_cluster_url}/{settings.mongo_database}"
    }};
    '''
    headers = {"Content-Type": "application/json"}
    try:
        resp = requests.post(url, json={"query": sql}, headers=headers)
        logger.info("Datasource creation response", response=resp.text)
        if resp.status_code not in (200, 201, 409):
            logger.error("Failed to create datasource", details=resp.text)
            return False
        logger.info("Datasource created or already exists", name=DEFAULT_DATASOURCE)
        return resp.json()
    except Exception as e:
        logger.error("Error creating datasource via SQL API", error=str(e))
        return False
