import json
import asyncio
from aiokafka import AIOKafkaConsumer
from collections import defaultdict, deque
from app.core.database import get_db
from app.models.symbol_averages import SymbolAverages
from app.models.raw_market_data import RawMarketData
import logging

logger = logging.getLogger("uvicorn")

price_cache = defaultdict(lambda: deque(maxlen=5))
consumer: AIOKafkaConsumer = None


async def save_moving_average(symbol: str, avg: float):
    session_gen = get_db()
    session = await anext(session_gen)
    try:
        ma = SymbolAverages(symbol=symbol, average=avg)
        session.add(ma)
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def save_raw_data(symbol: str, provider: str, price: float, raw: dict):
    session_gen = get_db()
    session = await anext(session_gen)
    try:
        ma = RawMarketData(symbol=symbol, provider=provider, price=price, raw_json=raw)
        session.add(ma)
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def process_message(data: dict):
    key = data["symbol"]
    provider = data["provider"]
    price = data["price"]
    price_cache[key].append(price)

    await save_raw_data(key, provider, price, data["data"])

    if len(price_cache[key]) == 5:
        avg = sum(price_cache[key]) / 5 # Using the last 5 for average
        logger.info(f"avg: {avg}")
        await save_moving_average(key, avg)


async def start_consumer():
    global consumer
    max_retries = 10
    retry_count = 0

    while retry_count < max_retries:
        try:
            consumer = AIOKafkaConsumer(
                "price-events",
                bootstrap_servers="broker:9092",
                group_id="Kafka_Consumer",
                auto_offset_reset="earliest",
                value_deserializer=lambda x: json.loads(x.decode("utf-8")),
                enable_auto_commit=True,
                consumer_timeout_ms=1000,
            )
            await consumer.start()
            await asyncio.sleep(1)  # ensure partitions are assigned

            logger.info("✅ Kafka consumer started")
            logger.info(f"Subscribed topics: {consumer.subscription()}")
            logger.info(f"Consumer group: {consumer._group_id}")
            return
        except Exception as e:
            retry_count += 1
            logger.info(f"⚠️ Attempt {retry_count}: Waiting for Kafka: {e}")
            await asyncio.sleep(5)

    raise Exception("Failed to connect to Kafka after maximum retries")


async def kafka_loop():
    global consumer
    await start_consumer()
    logger.info("in function kafka_loop")

    try:
        async for message in consumer:
            try:
                logger.info(f"Received: {message.value}")
                await process_message(message.value)
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                continue
    except Exception as e:
        logger.error(f"Consumer loop error: {e}")
    finally:
        if consumer:
            await consumer.stop()
            logger.info("🔻 Kafka consumer stopped")


def start_consumer_loop():
    logger.info("🟢 Starting Kafka consumer loop")
    return asyncio.create_task(kafka_loop())


def shutdown_consumer():
    global consumer
    if consumer:
        asyncio.create_task(consumer.stop())
        print("🔻 Shutdown consumer task started")
