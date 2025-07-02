# scripts/init_db.py
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
from app.core.database import engine, Base
from app.models import *  # loads all models


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(init_models())
