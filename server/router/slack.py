import os
import structlog
from fastapi import APIRouter, Request
from settings import Settings
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from mindsdb import store_slack_message, store_slack_thread_message
from mindsdb import gemini_retrieve_answer, shopify_text2sql_answer

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
        # Store the mention event
        store_slack_message(channel, text)
        try:
            slack_client.chat_postMessage(channel=channel, text="Working on it...", thread_ts=thread_ts)
        except SlackApiError as e:
            logger.error("Failed to send 'working on it' reply via Slack SDK", error=str(e))
        try:
            # Decide which retriever to use based on question type
            if any(word in clean_text.lower() for word in ["order", "shopify", "product", "customer"]):
                answer = shopify_text2sql_answer(clean_text)
            else:
                # Optionally fetch previous messages for context (not implemented, pass None)
                answer = gemini_retrieve_answer(clean_text, previous_messages=None)
        except Exception as e:
            logger.error("Retriever error", error=str(e))
            answer = f"Sorry, I couldn't process your request. Error: {str(e)}"
        try:
            slack_client.chat_postMessage(channel=channel, text=answer, thread_ts=thread_ts)
        except SlackApiError as e:
            logger.error("Failed to send reply via Slack SDK", error=str(e))
        return {"ok": True}

    # Handle thread replies (message events in a thread, not from a bot)
    elif event_type == "message" and thread_ts and not event.get("bot_id"):
        logger.info("Handling thread reply", text=text, user=user, channel=channel, thread_ts=thread_ts)
        # Store the thread reply event
        store_slack_thread_message(channel, thread_ts, text)
        try:
            slack_client.chat_postMessage(channel=channel, text="Working on it...", thread_ts=thread_ts)
        except SlackApiError as e:
            logger.error("Failed to send 'working on it' reply via Slack SDK", error=str(e))
        try:
            # Decide which retriever to use based on question type
            if any(word in text.lower() for word in ["order", "shopify", "product", "customer"]):
                # answer = shopify_text2sql_answer(text)
                answer = gemini_retrieve_answer(clean_text, previous_messages=None)
            else:
                # Optionally fetch previous messages for context (not implemented, pass None)
                answer = gemini_retrieve_answer(text, previous_messages=None)
        except Exception as e:
            logger.error("Retriever error", error=str(e))
            answer = f"Sorry, I couldn't process your request. Error: {str(e)}"
        try:
            slack_client.chat_postMessage(channel=channel, text=answer, thread_ts=thread_ts)
        except SlackApiError as e:
            logger.error("Failed to send reply via Slack SDK", error=str(e))
        return {"ok": True}

    # Optionally: handle direct messages (message.im)
    # elif event_type == "message" and event.get("channel_type") == "im":
    #     ...

    return {"ok": True}
