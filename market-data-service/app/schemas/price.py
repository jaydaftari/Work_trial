from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime


class PriceResponse(BaseModel):
    symbol: str
    price: float
    timestamp: datetime
    provider: str


class Test(BaseModel):
    test: str


class PollRequest(BaseModel):
    symbols: List[str] = Field(..., description="List of ticker symbols to poll")
    interval: int = Field(..., description="Polling interval in seconds")
    provider: Optional[str] = Field(
        None, description="Preferred data provider (optional)"
    )


class PollAcceptedResponse(BaseModel):
    job_id: UUID
    status: str
    config: Dict[str, object]


class StopRequest(BaseModel):
    job_id: str
