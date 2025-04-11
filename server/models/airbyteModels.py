from pydantic import BaseModel
from typing import Optional

class TokenRequest(BaseModel):
    client_id: str
    client_secret: str
    grant_type: Optional[str] = "client_credentials"

class TokenResponse(BaseModel):
    access_token: str

class MotherDuckConfigRequest(BaseModel):
    workspaceId: str
    motherduck_api_key: str
    destination_path: str
    schema: str

class CoinAPIConfig(BaseModel):
    api_key: str
    symbol_id: str

class SyncConfig(BaseModel):
    sourceId: str
    destinationId: str