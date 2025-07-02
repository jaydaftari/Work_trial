# app/models/poll_job.py
from sqlalchemy import Column, String, Integer, DateTime
from app.core.database import Base
from sqlalchemy.sql import func
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID


class PollJob(Base):
    __tablename__ = "poll_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    symbols = Column(String)  # comma-separated
    interval = Column(Integer)  # in seconds
    provider = Column(String)
    status = Column(String, default="accepted")
    created_at = Column(DateTime(timezone=True), default=func.now())
