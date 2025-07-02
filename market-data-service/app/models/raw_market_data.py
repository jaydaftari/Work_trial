# app/models/raw_market_data.py
from sqlalchemy import Column, String, DateTime, Float
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from uuid import uuid4
from app.core.database import Base


class RawMarketData(Base):
    __tablename__ = "raw_market_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    symbol = Column(String, index=True)
    provider = Column(String)
    price = Column(Float)
    # timestamp = Column(DateTime, index=True)
    raw_json = Column(JSONB)
    created_at = Column(DateTime(timezone=True), default=func.now())
