import os
import structlog
import hmac
import hashlib
import re
from fastapi import APIRouter, Request, HTTPException
import requests
from settings import Settings

logger = structlog.get_logger(__name__)
settings = Settings()

slack_router = APIRouter(prefix="/slack", tags=["slack"])

SLACK_SIGNING_SECRET = settings.slack_signing_secret
SLACK_BOT_TOKEN = settings.slack_client_secret
MINDSDB_API = settings.mindsdb_url.rstrip('/')
PROJECT = "slack_project"
CHATBOT = "startupslack"

# Helper: Verify Slack signature
def verify_slack_signature(request: Request, body: bytes) -> bool:
    timestamp = request.headers.get('X-Slack-Request-Timestamp')
    slack_signature = request.headers.get('X-Slack-Signature')
    if not timestamp or not slack_signature:
        return False
    sig_basestring = f"v0:{timestamp}:{body.decode()}"
    my_signature = 'v0=' + hmac.new(
        SLACK_SIGNING_SECRET.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(my_signature, slack_signature)

# Helper: Post message back to Slack
def post_to_slack(channel, text, thread_ts=None):
    url = "https://slack.com/api/chat.postMessage"
    headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}", "Content-Type": "application/json"}
    payload = {"channel": channel, "text": text}
    if thread_ts:
        payload["thread_ts"] = thread_ts
    r = requests.post(url, json=payload, headers=headers)
    return r.ok

@slack_router.post("/events")
async def slack_events(request: Request):
    body = await request.body()
    if not verify_slack_signature(request, body):
        logger.error("Invalid Slack signature")
        raise HTTPException(status_code=403, detail="Invalid signature")
    data = await request.json()
    # Slack URL verification challenge
    if data.get("type") == "url_verification":
        return {"challenge": data["challenge"]}
    # Only handle event callbacks
    event = data.get("event", {})
    event_type = event.get("type")
    # Thread support: get thread_ts if present
    thread_ts = event.get("thread_ts") or event.get("ts")

    # Detect intent for forecasting
    forecast_keywords = ["forecast", "predict sales", "future orders", "sales next week", "sales prediction"]
    text_lower = event.get("text", "").lower()
    if any(kw in text_lower for kw in forecast_keywords):
        # Call forecast endpoint
        try:
            from mindsdb.forecast_setup import forecast_router  # Avoid circular import
            import requests
            forecast_api = "http://localhost:8000/api/forecast/query"  # Adjust if running elsewhere
            resp = requests.post(forecast_api)
            if resp.status_code == 200:
                forecast_result = resp.json()
                answer = f"Sales forecast: {forecast_result}"
            else:
                answer = f"[Forecast error: {resp.text}]"
        except Exception as e:
            logger.error("Forecasting error", error=str(e))
            answer = "Sorry, I couldn't get a forecast right now."
        post_to_slack(event["channel"], answer, thread_ts)
        return {"ok": True}

    if event_type == "message" and not event.get("bot_id"):
        channel = event["channel"]
        user = event["user"]
        text = event["text"]
        # Query MindsDB chatbot
        try:
            resp = requests.post(f"{MINDSDB_API}/api/projects/{PROJECT}/chatbots/{CHATBOT}/completions", json={"question": text, "user": user})
            if resp.status_code == 200:
                answer = resp.json().get("answer", "[No answer returned]")
            else:
                answer = f"[MindsDB error: {resp.text}]"
        except Exception as e:
            logger.error("MindsDB chatbot error", error=str(e))
            answer = "Sorry, I couldn't process your request."
        post_to_slack(channel, answer, thread_ts)
    elif event_type == "app_mention":
        channel = event["channel"]
        user = event["user"]
        text = event.get("text", "")
        # Remove bot mention from text
        text = text.split('>', 1)[-1].strip() if '>' in text else text
        try:
            resp = requests.post(f"{MINDSDB_API}/api/projects/{PROJECT}/chatbots/{CHATBOT}/completions", json={"question": text, "user": user})
            if resp.status_code == 200:
                answer = resp.json().get("answer", "[No answer returned]")
            else:
                answer = f"[MindsDB error: {resp.text}]"
        except Exception as e:
            logger.error("MindsDB chatbot error", error=str(e))
            answer = "Sorry, I couldn't process your request."
        post_to_slack(channel, answer, thread_ts)
    elif event_type == "reaction_added":
        channel = event["item"]["channel"]
        reaction = event["reaction"]
        user = event["user"]
        # Example: respond to a reaction
        post_to_slack(channel, f"Thanks for the :{reaction}:, <@{user}>!", thread_ts)
    return {"ok": True}
