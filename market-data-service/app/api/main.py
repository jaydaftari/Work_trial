from fastapi import FastAPI
from app.api.routes import prices
from app.services.kafka.consumer import start_consumer_loop, shutdown_consumer
import os
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError
import logging

logger = logging.getLogger("uvicorn")

app = FastAPI()

consumer_task = None


KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "broker:9092")
TOPIC_NAME = os.environ.get("TOPIC_NAME", "price-events")
TOPIC_PARTITIONS = int(os.environ.get("TOPIC_PARTITIONS", 1))
TOPIC_REPLICATION_FACTOR = int(os.environ.get("TOPIC_REPLICATION_FACTOR", 1))


def create_topic():
    admin_client = KafkaAdminClient(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS, client_id="topic_creator"
    )

    topic = NewTopic(
        name=TOPIC_NAME,
        num_partitions=TOPIC_PARTITIONS,
        replication_factor=TOPIC_REPLICATION_FACTOR,
    )

    try:
        admin_client.create_topics([topic])
        print(f"✅ Created topic '{TOPIC_NAME}'")
    except TopicAlreadyExistsError:
        print(f"⚠️ Topic '{TOPIC_NAME}' already exists")
    finally:
        admin_client.close()


@app.on_event("startup")
async def startup_event():
    logger.info("Inside_startup")
    try:
        create_topic()
        global consumer_task
        consumer_task = start_consumer_loop()  # Remove await here
    except Exception as e:
        logger.info(f"Startup failed: {e}")
        print(f"Startup failed: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    global consumer_task
    if consumer_task:
        consumer_task.cancel()
    shutdown_consumer()


app.include_router(prices.router)


@app.get("/")
async def root():
    return {"message": "Market Data API running with Kafka consumer"}
