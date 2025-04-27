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
        r = requests.post(f"{MINDSDB_API}/sql/query", json={"query": sql})
        if r.status_code == 200:
            data = r.json().get("data", [])
            if data and 'answer' in data[0]:
                return data[0]['answer']
            else:
                return "[No answer returned]"
        else:
            return f"[Gemini SQL error: {r.text}]"
    except Exception as e:
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
        r = requests.post(f"{MINDSDB_API}/sql/query", json={"query": sql})
        if r.status_code == 200:
            data = r.json().get("data", [])
            if data and 'answer' in data[0]:
                return data[0]['answer']
            else:
                return "[No answer returned]"
        else:
            return f"[Polygon chatbot SQL error: {r.text}]"
    except Exception as e:
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
        r = requests.post(f"{MINDSDB_API}/sql/query", json={"query": sql})
        if r.status_code == 200:
            records = r.json().get("data", [])
            if not records:
                return "[No predictions returned]"
            # format date:price lines
            lines = [f"{rec.get('date', rec.get('day'))}: {rec.get('price')}" for rec in records]
            return "\n".join(lines)
        else:
            return f"[Price forecast SQL error: {r.text}]"
    except Exception as e:
        return f"Sorry, I couldn't process your request. Price forecast error: {str(e)}"