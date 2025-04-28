import structlog
from fastapi import APIRouter, Request
from settings import Settings
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from mindsdb import store_slack_message, store_slack_thread_message
import re
from mindsdb import polygon_text2sql_answer, gemini_retrieve_answer, make_prediction, langchain_completion

logger = structlog.get_logger(__name__)
settings = Settings()

slack_client = WebClient(token=settings.slack_bot_token)

slack_router = APIRouter(prefix="/slack", tags=["slack"])

@slack_router.post("/events")
async def slack_events(request: Request):
    # raw body logging removed to reduce verbosity
    try:
        data = await request.json()
    except Exception as e:
        logger.error("Failed to parse JSON from Slack event", error=str(e))
        return {"error": "Invalid JSON"}
    # Log only minimal event info
    event = data.get("event", {})
    logger.info("Incoming Slack event", type=event.get("type"), user=event.get("user"), channel=event.get("channel"), text=event.get("text", ""), thread_ts=event.get("thread_ts") or event.get("ts"))
    if data.get("type") == "url_verification":
        logger.info("Responding to Slack challenge", challenge=data.get("challenge"))
        return {"challenge": data["challenge"]}

    event = data.get("event", {})
    event_type = event.get("type")
    thread_ts = event.get("thread_ts") or event.get("ts")
    user = event.get("user")
    channel = event.get("channel")
    text = event.get("text", "")

    def parse_trade_message(text):
        pattern = r"/trade\\s+(\\w+)\\s+(Buy|Sell)\\s+([\\d.]+)\\s+([\\d.]+)\\s+([\\d.]+)\\s+([\\d.]+)\\s+([^\\s]+)\\s*(.*)"
        match = re.match(pattern, text)
        if not match:
            return None
        return {
            "symbol": match.group(1),
            "direction": match.group(2),
            "size": float(match.group(3)),
            "entry_price": float(match.group(4)),
            "stop_loss": float(match.group(5)),
            "take_profit": float(match.group(6)),
            "datetime": match.group(7),
            "notes": match.group(8),
        }

    # Handle trade journal entry via Slack command
    trade_data = parse_trade_message(text)
    if trade_data:
        try:
            entry = TradeJournalEntry(**trade_data)
            db[MONGO_COLLECTION].insert_one(entry.dict())
            slack_client.chat_postMessage(channel=channel, text="✅ Trade journal entry saved!", thread_ts=thread_ts)
        except Exception as e:
            slack_client.chat_postMessage(channel=channel, text=f"❌ Failed to save trade: {str(e)}", thread_ts=thread_ts)
        return {"ok": True}

    # Handle mentions (app_mention)
    if event_type == "app_mention":
        logger.info("Handling app_mention event", text=text, user=user, channel=channel)
        # Strip bot mention prefix regardless of ID
        clean_text = re.sub(r"^<@[^>]+>\s*", "", text).strip()
        # Store the mention event
        store_slack_message(channel, text)
        try:
            slack_client.chat_postMessage(channel=channel, text="Working on it...", thread_ts=thread_ts)
        except SlackApiError as e:
            logger.error("Failed to send 'working on it' reply via Slack SDK", error=str(e))
        try:
            # Explicit command prefix detection
            prefix_match = re.match(r"^(forecast|predict|trade|advisor|advice|analysis)[:\s]+(.+)", clean_text, re.IGNORECASE)
            if prefix_match:
                key, content = prefix_match.group(1).lower(), prefix_match.group(2).strip()
                if key in ("forecast", "predict"):
                    answer = make_prediction(content)
                elif key == "trade":
                    answer = polygon_text2sql_answer(content)
                else:
                    answer = langchain_completion(content)
            else:
                lower = clean_text.lower()
                if "forecast" in lower or "predict" in lower:
                    answer = make_prediction(clean_text)
                elif any(word in lower for word in ["order", "trade", "buy", "sell", "position", "stop", "take profit"]):
                    answer = polygon_text2sql_answer(clean_text)
                elif any(k in lower for k in ["advice", "recommend", "analysis"]):
                    answer = langchain_completion(clean_text)
                else:
                    answer = gemini_retrieve_answer(clean_text, previous_messages=None)
        except Exception as e:
            logger.error("Retriever error", error=str(e))
            answer = f"Sorry, I couldn't process your request. Error: {str(e)}"
        # Log outgoing reply
        logger.info("Sending Slack reply", text=answer, channel=channel, thread_ts=thread_ts)
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
            # Explicit command prefix detection
            prefix_match = re.match(r"^(forecast|predict|trade|advisor|advice|analysis)[:\s]+(.+)", text, re.IGNORECASE)
            if prefix_match:
                key, content = prefix_match.group(1).lower(), prefix_match.group(2).strip()
                if key in ("forecast", "predict"):
                    answer = make_prediction(content)
                elif key == "trade":
                    answer = polygon_text2sql_answer(content)
                else:
                    answer = langchain_completion(content)
            else:
                lower = text.lower()
                if "forecast" in lower or "predict" in lower:
                    answer = make_prediction(text)
                elif any(word in lower for word in ["order", "trade", "buy", "sell", "position", "stop", "take profit"]):
                    answer = polygon_text2sql_answer(text)
                elif any(k in lower for k in ["advice", "recommend", "analysis"]):
                    answer = langchain_completion(text)
                else:
                    answer = gemini_retrieve_answer(text, previous_messages=None)
        except Exception as e:
            logger.error("Retriever error", error=str(e))
            answer = f"Sorry, I couldn't process your request. Error: {str(e)}"
        # Log outgoing reply
        logger.info("Sending Slack reply", text=answer, channel=channel, thread_ts=thread_ts)
        try:
            slack_client.chat_postMessage(channel=channel, text=answer, thread_ts=thread_ts)
        except SlackApiError as e:
            logger.error("Failed to send reply via Slack SDK", error=str(e))
        return {"ok": True}

    return {"ok": True}
