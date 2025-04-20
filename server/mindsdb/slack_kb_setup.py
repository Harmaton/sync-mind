import structlog
import requests
from settings import Settings

logger = structlog.get_logger(__name__)
settings = Settings()

MINDSDB_API = settings.mindsdb_url.rstrip('/')
DEFAULT_PROJECT = "slack_project"
DEFAULT_DATASOURCE = "shopify_mongo"
DEFAULT_KB = "slack_kb"
DEFAULT_MODEL = "shopify_model"
DEFAULT_AGENT = "slack_agent"
DEFAULT_MONGO_COLLECTION = "shopify_collection"  # Change if needed
DEFAULT_PREDICT_FIELD = "target_field"  # Change to your actual target

def setup_slack_chatbot_kb():
    # 1. Create Project (as SQL CREATE DATABASE)
    try:
        sql = f"CREATE DATABASE {DEFAULT_PROJECT};"
        r = requests.post(f"{MINDSDB_API}/api/sql/query", json={"query": sql})
        if r.status_code not in (200, 201, 409):
            logger.error("Failed to create project (database)", details=r.text)
            return False
        logger.info("Project (database) created or already exists", name=DEFAULT_PROJECT)
    except Exception as e:
        logger.error("Error creating project (database)", error=str(e))
        return False

    # 2. Register MongoDB datasource (keep REST if no SQL equivalent)
    try:
        ds_payload = {
            "name": DEFAULT_DATASOURCE,
            "engine": "mongodb",
            "parameters": {
                "host": settings.mongo_cluster_url,
                "port": 27017,
                "username": settings.mongo_username,
                "password": settings.mongo_password,
                "database": settings.mongo_database
            }
        }
        r = requests.post(f"{MINDSDB_API}/api/datasources", json=ds_payload)
        if r.status_code not in (200, 201, 409):
            logger.error("Failed to register datasource", details=r.text)
            return False
        logger.info("Datasource registered or already exists", name=DEFAULT_DATASOURCE)
    except Exception as e:
        logger.error("Error registering datasource", error=str(e))
        return False

    # 3. Create Knowledge Base (if SQL supported, otherwise keep REST)
    try:
        sql = f"""
        CREATE KNOWLEDGE BASE {DEFAULT_PROJECT}.{DEFAULT_KB}
        FROM {DEFAULT_DATASOURCE};
        """
        r = requests.post(f"{MINDSDB_API}/api/sql/query", json={"query": sql})
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
