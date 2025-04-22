import os
import structlog
import hmac
import hashlib
import re
import requests
from fastapi import APIRouter, Request, HTTPException
from settings import Settings
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = structlog.get_logger(__name__)
settings = Settings()

SLACK_SIGNING_SECRET = settings.slack_signing_secret
SLACK_BOT_TOKEN = settings.slack_bot_token or os.environ.get("SLACK_BOT_TOKEN")
MINDSDB_API = settings.mindsdb_url.rstrip('/')
PROJECT = "mindsdb"
CHATBOT = "slack_chatbot"

slack_client = WebClient(token=settings.slack_bot_token)

slack_router = APIRouter(prefix="/slack", tags=["slack"])

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

@slack_router.post("/events")
async def slack_events(request: Request):
    body = await request.body()
    logger.info("Slack event raw body", body=body)
    try:
        data = await request.json()
    except Exception as e:
        logger.error("Failed to parse JSON from Slack event", error=str(e))
        return {"error": "Invalid JSON"}
    logger.info("Received Slack event", body=data)
    if data.get("type") == "url_verification":
        logger.info("Responding to Slack challenge", challenge=data.get("challenge"))
        return {"challenge": data["challenge"]}

    event = data.get("event", {})
    event_type = event.get("type")
    thread_ts = event.get("thread_ts") or event.get("ts")
    user = event.get("user")
    channel = event.get("channel")
    text = event.get("text", "")

    # Handle mentions (app_mention)
    if event_type == "app_mention":
        logger.info("Handling app_mention event", text=text, user=user, channel=channel)
        # Remove bot mention from text
        bot_user_id = settings.slack_bot_user_id or user
        mention = f"<@{bot_user_id}>"
        clean_text = text.replace(mention, "").strip()
        # 1. Immediately reply: Working on it...
        try:
            slack_client.chat_postMessage(channel=channel, text="Working on it...", thread_ts=thread_ts)
        except SlackApiError as e:
            logger.error("Failed to send 'working on it' reply via Slack SDK", error=str(e))
        # 2. Query MindsDB chatbot
        try:
            resp = requests.post(f"{MINDSDB_API}/api/projects/{PROJECT}/chatbots/{CHATBOT}/completions", json={"question": clean_text, "user": user})
            logger.info("MindsDB chatbot API response", status_code=resp.status_code, response=resp.text)
            if resp.status_code == 200:
                answer = resp.json().get("answer", "[No answer returned]")
            else:
                answer = f"[MindsDB error: {resp.text}]"
        except Exception as e:
            logger.error("MindsDB chatbot error", error=str(e))
            answer = f"Sorry, I couldn't process your request. MindsDB error: {str(e)}"
        # 3. Reply in thread using Slack SDK
        try:
            slack_client.chat_postMessage(channel=channel, text=answer, thread_ts=thread_ts)
        except SlackApiError as e:
            logger.error("Failed to send reply via Slack SDK", error=str(e))
        return {"ok": True}

    # Optionally: handle direct messages (message.im)
    # elif event_type == "message" and event.get("channel_type") == "im":
    #     ...

    return {"ok": True}
