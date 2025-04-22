import requests
import structlog
from settings import Settings

logger = structlog.get_logger(__name__)
settings = Settings()
MINDSDB_API = settings.mindsdb_url.rstrip('/')

def store_slack_message(channel_id: str, text: str):
    sql = f"""
    INSERT INTO slack_datasource.messages (channel_id, text)
    VALUES('{channel_id}', '{text.replace("'", "''")}')
    """
    r = requests.post(f"{MINDSDB_API}/sql/query", json={"query": sql})
    logger.info("Stored Slack message in datasource", response=r.text)
    return r.status_code in (200, 201, 409)

def store_slack_thread_message(channel_id: str, thread_ts: str, text: str):
    sql = f"""
    INSERT INTO slack_datasource.threads (channel_id, thread_ts, text)
    VALUES('{channel_id}', '{thread_ts}', '{text.replace("'", "''")}')
    """
    r = requests.post(f"{MINDSDB_API}/sql/query", json={"query": sql})
    logger.info("Stored Slack thread message in datasource", response=r.text)
    return r.status_code in (200, 201, 409)

def fetch_thread_messages(channel_id: str, thread_ts: str):
    """
    Fetch all messages in a specific Slack thread from the MindsDB slack_datasource.
    """
    sql = f"""
    SELECT * FROM slack_datasource.threads
    WHERE channel_id = '{channel_id}' AND thread_ts = '{thread_ts}';
    """
    r = requests.post(f"{MINDSDB_API}/sql/query", json={"query": sql})
    logger.info("Fetched Slack thread messages", response=r.text)
    if r.status_code == 200:
        try:
            return r.json().get("data", [])
        except Exception as e:
            logger.error("Error parsing thread fetch response", error=str(e))
            return []
    else:
        logger.error("Failed to fetch thread messages", status_code=r.status_code, details=r.text)
        return []
