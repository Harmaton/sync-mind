from pydantic import BaseModel
from typing import Optional

class TokenRequest(BaseModel):
    client_id: str
    client_secret: str
    grant_type: Optional[str] = "client_credentials"

class TokenResponse(BaseModel):
    access_token: str

class CoinAPIConfig(BaseModel):
    api_key: str
    symbol_id: str

class SyncConfig(BaseModel):
    sourceId: str
    destinationId: str

class PostgresConfig(BaseModel):
    username: str
    host: str
    password: str


class MongoDBConfig(BaseModel):
    workspaceId: str
    cluster_url: str
    database: str
    username: str
    password: str
