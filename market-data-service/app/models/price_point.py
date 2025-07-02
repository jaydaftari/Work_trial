from sqlalchemy import Column, String, Float, DateTime, UniqueConstraint
from app.core.database import Base
from sqlalchemy.sql import func


class PricePoint(Base):
    __tablename__ = "price_points"

    symbol = Column(String, primary_key=True)
    provider = Column(String, primary_key=True)
    price = Column(Float)
    timestamp = Column(DateTime(timezone=True), default=func.now())

    __table_args__ = (
        UniqueConstraint("symbol", "provider", name="uq_symbol_provider"),
    )
