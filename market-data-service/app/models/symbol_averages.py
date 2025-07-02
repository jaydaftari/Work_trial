# app/models/moving_average.py
from sqlalchemy import Column, String, Float, DateTime
from app.core.database import Base
from sqlalchemy.sql import func


class SymbolAverages(Base):
    __tablename__ = "symbol_averages"

    symbol = Column(String, primary_key=True)
    average = Column(Float)
    updated_at = Column(DateTime(timezone=True), default=func.now())
