import structlog
from .datasources import create_slack_datasource_in_mindsdb, create_mongo_datasource
from .engines import create_google_gemini_engine, create_forecast_engine
from .models import create_gemini_model, create_forecast_model
from .skills import (
    create_stocks_text2sql_skill
)
from .agents import (
    create_advisor_agent
)
from .chatbots import (
    create_advisor_chatbot
)

logger = structlog.get_logger(__name__)

def mindsdb_setup():
    if not create_mongo_datasource():
        logger.error("Failed to create Mongo datasource")
        return False
    if not create_slack_datasource_in_mindsdb():
        logger.error("Failed to create Slack datasource")
        return False
    if not create_stocks_text2sql_skill():
        logger.error("Failed to create Stocks text2sql skill")
        return False
    if not create_google_gemini_engine():
        logger.error("Failed to create Google Gemini engine")
        return False
    if not create_gemini_model():
        logger.error("Failed to create Gemini model")
        return False
    if not create_forecast_engine():
        logger.error("Failed to create Forecast engine")
        return False
    if not create_forecast_model():
        logger.error("Failed to create Forecast model")
        return False
    if not create_advisor_agent():
        logger.error("Failed to create Advisor agent")
        return False
    if not create_advisor_chatbot():
        logger.error("Failed to create Advisor chatbot")
        return False
    logger.info("Slack chatbot knowledge base and chatbot setup complete!")
    return True