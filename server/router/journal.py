import os
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from pymongo import MongoClient

# MongoDB connection setup (reuse from mongo_init.py logic)
MONGO_USER = os.environ.get("MONGO_USERNAME", "mindsuser")
MONGO_PASS = os.environ.get("MONGO_PASSWORD", "")
MONGO_CLUSTER = os.environ.get("MONGO_CLUSTER_URL", "mindcluster.qhsxpfc.mongodb.net")
MONGO_DB = os.environ.get("MONGO_DATABASE", "mindscluster")
MONGO_COLLECTION = os.environ.get("MONGO_COLLECTION", "trade_journals")

uri = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_CLUSTER}/{MONGO_DB}"
client = MongoClient(uri)
db = client[MONGO_DB]

journal_router = APIRouter(prefix="/journal", tags=["journal"])

class TradeJournalEntry(BaseModel):
    symbol: str
    direction: str  # 'Buy' or 'Sell'
    size: float
    entry_price: float
    stop_loss: float
    take_profit: float
    datetime: str  
    notes: str = ""

@journal_router.post("/", status_code=201)
async def create_trade_journal(entry: TradeJournalEntry):
    try:
        result = db[MONGO_COLLECTION].insert_one(entry.dict())
        return {"message": "Trade journal entry created", "id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create trade journal entry: {str(e)}")