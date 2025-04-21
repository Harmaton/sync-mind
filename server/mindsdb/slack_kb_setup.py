import structlog
import requests
from settings import Settings

logger = structlog.get_logger(__name__)
settings = Settings()

MINDSDB_API = settings.mindsdb_url.rstrip('/')
DEFAULT_PROJECT = "airbyte_hackathon"
DEFAULT_DATASOURCE = "shopify_mongo"
DEFAULT_KB = "slack_kb"
DEFAULT_MODEL = "shopify_model"
DEFAULT_AGENT = "slack_agent"
DEFAULT_MONGO_COLLECTION = "shopify_collection"  # Change if needed
DEFAULT_PREDICT_FIELD = "target_field"  # Change to your actual target

def create_slack_datasource():
    """
    Creates the Slack MongoDB datasource using MindsDB SQL API (CREATE DATABASE ... WITH ENGINE = 'mongodb').
    """
    from settings import Settings
    settings = Settings()
    url = f"{MINDSDB_API}/sql/query"
    sql = f'''
    CREATE DATABASE {DEFAULT_DATASOURCE}
    WITH
      ENGINE = 'mongodb',
      PARAMETERS = {{
        "host": "{settings.mongo_cluster_url}",
        "username": "{settings.mongo_username}",
        "password": "{settings.mongo_password}",
        "database": "{settings.mongo_database}"
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


def setup_slack_chatbot_kb():
    # 1. Create Datasource
    try:
        create_slack_datasource()
    except Exception as e:
        logger.error("Error creating datasource", error=str(e))
        return False

    # 2. Create Knowledge Base
    try:
        sql = f"CREATE KNOWLEDGE_BASE mindsdb.{DEFAULT_KB};"
        r = requests.post(f"{MINDSDB_API}/sql/query", json={"query": sql})
        logger.info("Knowledge base creation response", response=r.text)
        if r.status_code not in (200, 201, 409):
            logger.error("Failed to create knowledge base", details=r.text)
            return False
        logger.info("Knowledge base created or already exists", name=DEFAULT_KB)
    except Exception as e:
        logger.error("Error creating knowledge base", error=str(e))
        return False

    # 4. Create Model (SQL endpoint)
    try:
        sql = f"""
        CREATE MODEL {DEFAULT_PROJECT}.{DEFAULT_MODEL} 
        PREDICT {DEFAULT_PREDICT_FIELD} 
        USING engine = 'mongodb', datasource = '{DEFAULT_DATASOURCE}', table = '{DEFAULT_MONGO_COLLECTION}';
        """
        sql_payload = {"query": sql}
        r = requests.post(f"{MINDSDB_API}/api/sql/query", json=sql_payload)
        if r.status_code not in (200, 201, 409):
            logger.error("Failed to create model", details=r.text)
            return False
        logger.info("Model created or already exists", name=DEFAULT_MODEL)
    except Exception as e:
        logger.error("Error creating model", error=str(e))
        return False

    # 5. Create Agent (SQL if supported, else REST fallback)
    try:
        sql = f"""
        CREATE AGENT {DEFAULT_PROJECT}.{DEFAULT_AGENT}
        USING MODEL = '{DEFAULT_MODEL}', SKILLS = ['knowledge_base', 'text2sql'];
        """
        r = requests.post(f"{MINDSDB_API}/api/sql/query", json={"query": sql})
        if r.status_code not in (200, 201, 409):
            logger.error("Failed to create agent", details=r.text)
            return False
        logger.info("Agent created or already exists", name=DEFAULT_AGENT)
    except Exception as e:
        logger.error("Error creating agent", error=str(e))
        return False

    # 6. Create Chatbot (SQL if supported, else REST fallback)
    try:
        sql = f"""
        CREATE CHATBOT {DEFAULT_PROJECT}.startupslack
        USING DATABASE = '{DEFAULT_DATASOURCE}', AGENT = '{DEFAULT_AGENT}';
        """
        r = requests.post(f"{MINDSDB_API}/api/sql/query", json={"query": sql})
        if r.status_code not in (200, 201, 409):
            logger.error("Failed to create chatbot", details=r.text)
            return False
        logger.info("Chatbot created or already exists", name="startupslack")
    except Exception as e:
        logger.error("Error creating chatbot", error=str(e))
        return False

    logger.info("Slack chatbot knowledge base and chatbot setup complete!")
    return True
