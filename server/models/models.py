from datetime import datetime
from pydantic import BaseModel

class InsightsResponse(BaseModel):
    sales_trend: str
    customer_sentiment: str
    top_product: str

class PostgresDataSourceCreate(BaseModel):
    host: str
    port: int
    username: str
    password: str
    database: str

# Pydantic model for response
class SyncResponse(BaseModel):
    connection_id: str
    job_id: str
    status: str
    start_time: datetime
    duration: float
    records_synced: int
    bytes_synced: int
    job_url: str
    message: str
    

class MindsDBPingResponse(BaseModel):
    status: str

class HealthStatusResponse(BaseModel):
    status: str
    channel: str

