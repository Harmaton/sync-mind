import requests
from settings import Settings
import structlog

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

def shopify_text2sql_answer(question: str) -> str:
    """
    Query the shopify_chatbot in MindsDB to get an answer to the question using Text2SQL skill.
    """
    sql = f"""
    SELECT answer
    FROM shopify_chatbot
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
            return f"[Shopify chatbot SQL error: {r.text}]"
    except Exception as e:
        return f"Sorry, I couldn't process your request. Shopify chatbot error: {str(e)}"
