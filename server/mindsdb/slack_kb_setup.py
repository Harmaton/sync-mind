import structlog
import requests
from settings import Settings

logger = structlog.get_logger(__name__)
settings = Settings()

MINDSDB_API = settings.mindsdb_url.rstrip('/')
DEFAULT_PROJECT = "mindsdb"
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

def setup_slack_chatbot_kb():
    # 1. Create Datasource
    try:
        create_slack_datasource()
    except Exception as e:
        logger.error("Error creating datasource", error=str(e))
        return False

    # 2. Create Knowledge Base (with optional embedding model)
    try:
        sql = f"""
        CREATE KNOWLEDGE_BASE mindsdb.{DEFAULT_KB};
        """
        r = requests.post(f"{MINDSDB_API}/sql/query", json={"query": sql})
        logger.info("Knowledge base creation response", response=r.text)
        if r.status_code not in (200, 201, 409):
            logger.error("Failed to create knowledge base", details=r.text)
            return False
        logger.info("Knowledge base created or already exists", name=DEFAULT_KB)
    except Exception as e:
        logger.error("Error creating knowledge base", error=str(e))
        return False

    # 3. Populate Knowledge Base from MongoDB
    try:
        sql = f"""
        INSERT INTO mindsdb.{DEFAULT_KB} (content)
        SELECT orders AS content FROM {DEFAULT_DATASOURCE}.orders;
        """
        r = requests.post(f"{MINDSDB_API}/sql/query", json={"query": sql})
        logger.info("Knowledge base population response", response=r.text)
        if r.status_code not in (200, 201, 409):
            logger.error("Failed to populate knowledge base", details=r.text)
            return False
        logger.info("Knowledge base populated with MongoDB data", name=DEFAULT_KB)
    except Exception as e:
        logger.error("Error populating knowledge base", error=str(e))
        return False

    # 4. Create Knowledge Base Skill
    try:
        sql = f"""
        CREATE SKILL slack_kb_skill
        USING
            type = 'knowledge_base',
            source = 'mindsdb.{DEFAULT_KB}',
            description = 'Slack knowledge base for Shopify data';
        """
        r = requests.post(f"{MINDSDB_API}/sql/query", json={"query": sql})
        logger.info("Knowledge base skill creation response", response=r.text)
        if r.status_code not in (200, 201, 409):
            logger.error("Failed to create knowledge base skill", details=r.text)
            return False
        logger.info("Knowledge base skill created or already exists", name='slack_kb_skill')
    except Exception as e:
        logger.error("Error creating knowledge base skill", error=str(e))
        return False

    # 5. Create Text2SQL Skill
    try:
        sql = f"""
        CREATE SKILL slack_text2sql_skill
        USING
            type = 'text2sql',
            database = '{DEFAULT_DATASOURCE}',
            tables = ['orders'],
            description = 'Text-to-SQL skill for querying Shopify data in MongoDB.';
        """
        r = requests.post(f"{MINDSDB_API}/sql/query", json={"query": sql})
        logger.info("Text2SQL skill creation response", response=r.text)
        if r.status_code not in (200, 201, 409):
            logger.error("Failed to create Text2SQL skill", details=r.text)
            return False
        logger.info("Text2SQL skill created or already exists", name='slack_text2sql_skill')
    except Exception as e:
        logger.error("Error creating Text2SQL skill", error=str(e))
        return False

    # 6. Create Conversational Model (AI Model)
    try:
        sql = f"""
        CREATE MODEL slack_convo_model
        PREDICT answer
        USING
            engine = 'langchain',
            provider = 'gemini',
            gemini_api_key = '{settings.gemini_api_key}',
            model_name = 'gemini-pro',
            mode = 'conversational',
            user_column = 'question',
            assistant_column = 'answer',
            max_tokens = 100,
            temperature = 0,
            verbose = True,
            prompt_template = 'Answer the user input in a helpful way using tools';
        """
        r = requests.post(f"{MINDSDB_API}/sql/query", json={"query": sql})
        logger.info("Conversational model creation response", response=r.text)
        if r.status_code not in (200, 201, 409):
            logger.error("Failed to create conversational model", details=r.text)
            return False
        logger.info("Conversational model created or already exists", name='slack_convo_model')
    except Exception as e:
        logger.error("Error creating conversational model", error=str(e))
        return False

    # 7. Create Agent
    try:
        sql = f"""
        CREATE AGENT slack_agent
        USING
            model = 'slack_convo_model',
            skills = ['slack_kb_skill', 'slack_text2sql_skill'];
        """
        r = requests.post(f"{MINDSDB_API}/sql/query", json={"query": sql})
        logger.info("Agent creation response", response=r.text)
        if r.status_code not in (200, 201, 409):
            logger.error("Failed to create agent", details=r.text)
            return False
        logger.info("Agent created or already exists", name='slack_agent')
    except Exception as e:
        logger.error("Error creating agent", error=str(e))
        return False

    # 8.  Create Chatbot (if Slack DB exists)
    try:
        sql = f"""
        CREATE CHATBOT slack_chatbot
        USING
            database = '{DEFAULT_DATASOURCE}',
            agent = 'slack_agent',
            is_running = true;
        """
        r = requests.post(f"{MINDSDB_API}/sql/query", json={"query": sql})
        logger.info("Chatbot creation response", response=r.text)
        if r.status_code not in (200, 201, 409):
            logger.error("Failed to create chatbot", details=r.text)
            return False
        logger.info("Chatbot created or already exists", name='slack_chatbot')
    except Exception as e:
        logger.error("Error creating chatbot", error=str(e))
        return False

    # 9. Wire up  Slack chatbot setup
    # (Removed automatic hello message to channel on startup)
    return True

logger.info("Slack chatbot knowledge base and chatbot setup complete!")
