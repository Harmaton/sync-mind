import os
import structlog
import requests
from fastapi import APIRouter, Request
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
        bot_user_id = settings.slack_bot_user_id or user
        mention = f"<@{bot_user_id}>"
        clean_text = text.replace(mention, "").strip()
        try:
            slack_client.chat_postMessage(channel=channel, text="Working on it...", thread_ts=thread_ts)
        except SlackApiError as e:
            logger.error("Failed to send 'working on it' reply via Slack SDK", error=str(e))
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
        try:
            slack_client.chat_postMessage(channel=channel, text=answer, thread_ts=thread_ts)
        except SlackApiError as e:
            logger.error("Failed to send reply via Slack SDK", error=str(e))
        return {"ok": True}

    # Handle thread replies (message events in a thread, not from a bot)
    elif event_type == "message" and thread_ts and not event.get("bot_id"):
        logger.info("Handling thread reply", text=text, user=user, channel=channel, thread_ts=thread_ts)
        try:
            slack_client.chat_postMessage(channel=channel, text="Working on it...", thread_ts=thread_ts)
        except SlackApiError as e:
            logger.error("Failed to send 'working on it' reply via Slack SDK", error=str(e))
        try:
            resp = requests.post(f"{MINDSDB_API}/api/projects/{PROJECT}/chatbots/{CHATBOT}/completions", json={"question": text, "user": user})
            logger.info("MindsDB chatbot API response", status_code=resp.status_code, response=resp.text)
            if resp.status_code == 200:
                answer = resp.json().get("answer", "[No answer returned]")
            else:
                answer = f"[MindsDB error: {resp.text}]"
        except Exception as e:
            logger.error("MindsDB chatbot error", error=str(e))
            answer = f"Sorry, I couldn't process your request. MindsDB error: {str(e)}"
        try:
            slack_client.chat_postMessage(channel=channel, text=answer, thread_ts=thread_ts)
        except SlackApiError as e:
            logger.error("Failed to send reply via Slack SDK", error=str(e))
        return {"ok": True}

    # Optionally: handle direct messages (message.im)
    # elif event_type == "message" and event.get("channel_type") == "im":
    #     ...

    return {"ok": True}
