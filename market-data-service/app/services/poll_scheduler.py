import asyncio
import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from app.services.market_data import get_market_data
from app.models.poll_job import PollJob

# Active in-memory task registry
active_jobs = {}


async def polling_loop(symbols, interval, provider, job_id):
    try:
        while True:
            for symbol in symbols:
                try:
                    data = await get_market_data(symbol, provider=provider)
                    logging.info(f"[{job_id}] Sent {symbol} data to Kafka.")
                except Exception as e:
                    logging.warning(
                        f"[{job_id}] Error fetching/sending for {symbol}: {e}"
                    )
                await asyncio.sleep(1)
            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        logging.info(f"[{job_id}] Polling task cancelled.")
        raise
    finally:
        active_jobs.pop(job_id, None)
        logging.info(f"[{job_id}] Job cleaned up.")


async def schedule_polling_job(symbols, interval, provider, job_id):
    if job_id in active_jobs:
        raise ValueError(f"Polling job {job_id} already exists.")

    task = asyncio.create_task(polling_loop(symbols, interval, provider, job_id))
    active_jobs[job_id] = task
    return task


async def stop_polling_job(job_id: str, db: AsyncSession = None):
    task = active_jobs.get(job_id)
    if not task:
        raise ValueError(f"No active polling job with id {job_id}")

    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    if db:
        stmt = (
            update(PollJob)
            .where(PollJob.id == uuid.UUID(job_id))
            .values(status="closed")
        )
        await db.execute(stmt)
        await db.commit()
