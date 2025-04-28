import requests
from settings import Settings
import structlog
import re

logger = structlog.get_logger(__name__)
settings = Settings()
MINDSDB_API = settings.mindsdb_url.rstrip('/')

def gemini_retrieve_answer(question: str, previous_messages: list = None) -> str:
    """
    Query the Gemini model in MindsDB to get an answer to the question, optionally providing previous Slack messages as context.
    previous_messages: List of previous Slack messages (strings), or None.
    """
    # Compose context from previous messages if provided
    context = ""
    if previous_messages:
        context = "Previous Slack messages (for context):\n" + "\n".join(previous_messages) + "\n"
    full_question = f"{context}Current question: {question}"

    sql = f"""
    SELECT answer
    FROM google_gemini_model
    WHERE question = '{full_question.replace("'", "''")}';
    """
    try:
        logger.debug("Gemini SQL Query", sql=sql)
        r = requests.post(f"{MINDSDB_API}/sql/query", json={"query": sql})
        logger.debug("Gemini SQL Response", status_code=r.status_code, response=r.text)
        if r.status_code != 200:
            logger.error("Gemini SQL error", status=r.status_code, response=r.text)
            return f"[Gemini SQL error: {r.text}]"
        payload = r.json()
        data = payload.get("data", [])
        if not data or 'answer' not in data[0]:
            logger.warning("Gemini returned no answer", payload=payload)
            return "[No answer returned]"
        return data[0]['answer']
    except Exception as e:
        logger.error("Gemini exception", error=str(e))
        return f"Sorry, I couldn't process your request. Gemini error: {str(e)}"

def polygon_text2sql_answer(question: str) -> str:
    """
    Query the polygon_chatbot in MindsDB to get an answer to the question using Text2SQL skill.
    """
    sql = f"""
    SELECT answer
    FROM advisor_chatbot
    WHERE question = '{question.replace("'", "''")}';
    """
    try:
        logger.debug("Polygon SQL Query", sql=sql)
        r = requests.post(f"{MINDSDB_API}/sql/query", json={"query": sql})
        logger.debug("Polygon SQL Response", status_code=r.status_code, response=r.text)
        if r.status_code != 200:
            logger.error("Polygon SQL error", status=r.status_code, response=r.text)
            return f"[Polygon chatbot SQL error: {r.text}]"
        payload = r.json()
        data = payload.get("data", [])
        if not data or 'answer' not in data[0]:
            logger.warning("Polygon returned no answer", payload=payload)
            return "[No answer returned]"
        return data[0]['answer']
    except Exception as e:
        logger.error("Polygon exception", error=str(e))
        return f"Sorry, I couldn't process your request. Polygon chatbot error: {str(e)}"

def make_prediction(question: str) -> str:
    # parse date(s) in YYYY-MM-DD format
    dates = re.findall(r'\d{4}-\d{2}-\d{2}', question)
    if len(dates) == 1:
        start = end = dates[0]
    elif len(dates) >= 2:
        start, end = dates[0], dates[1]
    else:
        return "Please specify a date or date range in YYYY-MM-DD format."

    # build SQL for single date or date range
    if start == end:
        sql = f"""
        SELECT day AS date, price
        FROM price_forecast_model
        WHERE day = '{start}';
        """
    else:
        sql = f"""
        SELECT day AS date, price
        FROM price_forecast_model
        WHERE day >= '{start}' AND day <= '{end}';
        """

    try:
        logger.debug("Price forecast SQL Query", sql=sql)
        r = requests.post(f"{MINDSDB_API}/sql/query", json={"query": sql})
        logger.debug("Price forecast SQL Response", status_code=r.status_code, response=r.text)
        if r.status_code != 200:
            logger.error("Price forecast SQL error", status=r.status_code, response=r.text)
            return f"[Price forecast SQL error: {r.text}]"
        payload = r.json()
        records = payload.get("data", [])
        if not records:
            logger.warning("Price forecast returned no predictions", payload=payload)
            return "[No predictions returned]"
        # format date:price lines
        lines = [f"{rec.get('date', rec.get('day'))}: {rec.get('price')}" for rec in records]
        return "\n".join(lines)
    except Exception as e:
        logger.error("Price forecast exception", error=str(e))
        return f"Sorry, I couldn't process your request. Price forecast error: {str(e)}"

def langchain_completion(question: str) -> str:
    # Clean input to prevent SQL injection and log query
    escaped = question.replace("'", "''")
    sql = f"SELECT completion FROM langchain_openai_model WHERE question = '{escaped}' LIMIT 1"
    logger.debug("Langchain SQL Query", sql=sql)
    try:
        r = requests.post(f"{MINDSDB_API}/sql/query", json={"query": sql})
        logger.debug("Langchain SQL Response", status_code=r.status_code, response=r.text)
        if r.status_code != 200:
            logger.error("Langchain SQL error", status=r.status_code, response=r.text)
            return f"[Langchain SQL error: {r.text}]"
        payload = r.json()
        data = payload.get("data", [])
        if not data or 'completion' not in data[0]:
            logger.warning("Langchain returned no completion", payload=payload)
            return "[No answer returned]"
        return data[0]['completion']
    except Exception as e:
        logger.error("Langchain exception", error=str(e))
        return f"Sorry, I couldn't process your request. Langchain error: {str(e)}"