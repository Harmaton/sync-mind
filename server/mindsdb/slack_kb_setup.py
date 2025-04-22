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
DEFAULT_MONGO_COLLECTION = "shopify_collection"  
DEFAULT_PREDICT_FIELD = "target_field"

def create_slack_datasource_in_mindsdb():
    """
    Create the Slack datasource in MindsDB using SQL API.
    """
    sql = f"""
    CREATE DATABASE slack_datasource
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
        create_slack_datasource_in_mindsdb()
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
        INSERT INTO mindsdb.{DEFAULT_KB}
            SELECT text AS content FROM {DEFAULT_DATASOURCE}.orders;
        """
        r = requests.post(f"{MINDSDB_API}/sql/query", json={"query": sql})
        logger.info("Knowledge base population response", response=r.text)
        if r.status_code not in (200, 201, 409):
            logger.error("Failed to populate knowledge base", details=r.text)
            return False
        logger.info("Knowledge base populated or already up-to-date", name=DEFAULT_KB)
    except Exception as e:
        logger.error("Error populating knowledge base", error=str(e))
        return False

    # 4. Create text2sql skill
    try:
        sql = f"""
        CREATE SKILL text_to_sql_skill
        USING
            type = 'text2sql',
            database = '{settings.mongo_database}',
            tables = ['orders', 'products'],
            description = "This is order data";
        """
        r = requests.post(f"{MINDSDB_API}/sql/query", json={"query": sql})
        logger.info("text2sql skill creation response", response=r.text)
        if r.status_code not in (200, 201, 409):
            logger.error("Failed to create text2sql skill", details=r.text)
            return False
        logger.info("text2sql skill created or already exists")
    except Exception as e:
        logger.error("Error creating text2sql skill", error=str(e))
        return False

    # 5. Create knowledge base skill
    try:
        sql = f"""
        CREATE SKILL kb_skill
        USING
            type = 'knowledge_base',
            source = '{DEFAULT_KB}',
            description = 'Order and support knowledge base';
        """
        r = requests.post(f"{MINDSDB_API}/sql/query", json={"query": sql})
        logger.info("Knowledge base skill creation response", response=r.text)
        if r.status_code not in (200, 201, 409):
            logger.error("Failed to create knowledge base skill", details=r.text)
            return False
        logger.info("Knowledge base skill created or already exists")
    except Exception as e:
        logger.error("Error creating knowledge base skill", error=str(e))
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
            skills = ['kb_skill', 'text_to_sql_skill'];
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

    # 8. Create Gemini Engine
    try:
        sql = f"""
        CREATE ML_ENGINE google_gemini_engine
        FROM google_gemini
        USING
            api_key = '{settings.gemini_api_key}';
        """
        r = requests.post(f"{MINDSDB_API}/sql/query", json={"query": sql})
        logger.info("Gemini engine creation response", response=r.text)
        if r.status_code not in (200, 201, 409):
            logger.error("Failed to create Gemini engine", details=r.text)
            return False
        logger.info("Gemini engine created or already exists", name='google_gemini_engine')
    except Exception as e:
        logger.error("Error creating Gemini engine", error=str(e))
        return False

    # 9. Create Gemini Model
    try:
        sql = f"""
        CREATE MODEL google_gemini_model
        PREDICT answer
        USING
            engine = 'google_gemini_engine',
            column = 'question',
            model = 'gemini-pro';
        """
        r = requests.post(f"{MINDSDB_API}/sql/query", json={"query": sql})
        logger.info("Gemini model creation response", response=r.text)
        if r.status_code not in (200, 201, 409):
            logger.error("Failed to create Gemini model", details=r.text)
            return False
        logger.info("Gemini model created or already exists", name='google_gemini_model')
    except Exception as e:
        logger.error("Error creating Gemini model", error=str(e))
        return False

    # 10.  Create Chatbot (if Slack DB exists)
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

    # 11. Wire up  Slack chatbot setup
    # (Removed automatic hello message to channel on startup)
    
    # 12. --- LangChain Engine and Model for Shopify/MongoDB Text2SQL Chatbot ---
    try:
        sql = f"""
        CREATE ML_ENGINE langchain_engine
        FROM langchain
        USING
            openai_api_key = '{settings.openai_api_key}';
        """
        r = requests.post(f"{MINDSDB_API}/sql/query", json={"query": sql})
        logger.info("LangChain engine creation response", response=r.text)
        if r.status_code not in (200, 201, 409):
            logger.error("Failed to create LangChain engine", details=r.text)
            return False
        logger.info("LangChain engine created or already exists", name='langchain_engine')
    except Exception as e:
        logger.error("Error creating LangChain engine", error=str(e))
        return False

    # 13. Create LangChain Conversational Model
    try:
        sql = f"""
        CREATE MODEL shopify_convo_model
        PREDICT answer
        USING
            engine = 'langchain_engine',
            input_column = 'question',
            model_name = 'gpt-4',
            mode = 'conversational',
            user_column = 'question',
            assistant_column = 'answer',
            max_tokens = 100,
            temperature = 0,
            verbose = True,
            prompt_template = 'Answer the user input in a helpful way using tools';
        """
        r = requests.post(f"{MINDSDB_API}/sql/query", json={"query": sql})
        logger.info("Shopify LangChain model creation response", response=r.text)
        if r.status_code not in (200, 201, 409):
            logger.error("Failed to create Shopify LangChain model", details=r.text)
            return False
        logger.info("Shopify LangChain model created or already exists", name='shopify_convo_model')
    except Exception as e:
        logger.error("Error creating Shopify LangChain model", error=str(e))
        return False

    # 14. Create Text2SQL Skill for Shopify/MongoDB
    try:
        sql = f"""
        CREATE SKILL shopify_text2sql_skill
        USING
            type = 'text2sql',
            database = '{DEFAULT_DATASOURCE}',
            tables = ['orders','products','customers'],
            description = 'Shopify orders and customer data';
        """
        r = requests.post(f"{MINDSDB_API}/sql/query", json={"query": sql})
        logger.info("Shopify Text2SQL skill creation response", response=r.text)
        if r.status_code not in (200, 201, 409):
            logger.error("Failed to create Shopify Text2SQL skill", details=r.text)
            return False
        logger.info("Shopify Text2SQL skill created or already exists", name='shopify_text2sql_skill')
    except Exception as e:
        logger.error("Error creating Shopify Text2SQL skill", error=str(e))
        return False

    # 15. Create Agent for Shopify/MongoDB
    try:
        sql = f"""
        CREATE AGENT shopify_agent
        USING
            model = 'shopify_convo_model',
            skills = ['shopify_text2sql_skill'];
        """
        r = requests.post(f"{MINDSDB_API}/sql/query", json={"query": sql})
        logger.info("Shopify agent creation response", response=r.text)
        if r.status_code not in (200, 201, 409):
            logger.error("Failed to create Shopify agent", details=r.text)
            return False
        logger.info("Shopify agent created or already exists", name='shopify_agent')
    except Exception as e:
        logger.error("Error creating Shopify agent", error=str(e))
        return False

    # 16. Create Shopify Chatbot (Text2SQL)
    try:
        sql = f"""
        CREATE CHATBOT shopify_chatbot
        USING
            database = '{DEFAULT_DATASOURCE}',
            agent = 'shopify_agent',
            is_running = true;
        """
        r = requests.post(f"{MINDSDB_API}/sql/query", json={"query": sql})
        logger.info("Shopify chatbot creation response", response=r.text)
        if r.status_code not in (200, 201, 409):
            logger.error("Failed to create Shopify chatbot", details=r.text)
            return False
        logger.info("Shopify chatbot created or already exists", name='shopify_chatbot')
    except Exception as e:
        logger.error("Error creating Shopify chatbot", error=str(e))
        return False

    return True

logger.info("Slack chatbot knowledge base and chatbot setup complete!")
