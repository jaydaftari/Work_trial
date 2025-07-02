from kafka import KafkaProducer

# from aiokafka import AIOKafkaProducer
import json

producer = None


def get_producer():
    global producer
    if producer is None:
        producer = KafkaProducer(
            bootstrap_servers="broker:9092",  # Use 'kafka' if in docker-compose; localhost if local
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
    return producer


def on_send_success(record_metadata):
    print(
        f"Message delivered to {record_metadata.topic} partition {record_metadata.partition} at offset {record_metadata.offset}"
    )


def on_send_error(excp):
    print(f"Error sending message: {excp}")


def send_price_data(topic: str, data: dict, symbol: str, provider: str, price: float):
    enriched_data = {
        "symbol": symbol,
        "provider": provider,
        "price": price,
        "data": data,
    }
    producer = get_producer()
    producer.send(topic, enriched_data)
    producer.send(topic, enriched_data).add_callback(on_send_success).add_errback(
        on_send_error
    )
    producer.flush()


# from aiokafka import AIOKafkaProducer
# import json
# import asyncio

# producer = None

# async def get_producer():
#     global producer
#     try:
#         if producer is None:
#             producer = AIOKafkaProducer(
#                 bootstrap_servers="broker:9092",  # Use 'kafka' if in docker-compose; localhost if local
#                 value_serializer=lambda v: json.dumps(v).encode("utf-8"),
#             )
#             await producer.start()
#         return producer
#     except Exception as e:
#         print(f"Error creating producer: {e}")
#         raise

# async def close_producer():
#     global producer
#     if producer is not None:
#         await producer.stop()
#         producer = None

# def on_send_success(record_metadata):
#     print(
#         f"Message delivered to {record_metadata.topic} partition {record_metadata.partition} at offset {record_metadata.offset}"
#     )

# def on_send_error(excp):
#     print(f"Error sending message: {excp}")

# async def send_price_data(topic: str, data: dict, symbol: str, provider: str, price: float):
#     enriched_data = {
#         "symbol": symbol,
#         "provider": provider,
#         "price": price,
#         "data": data,
#     }

#     try:
#         producer = await get_producer()

#         # Send message and await the result
#         record_metadata = await producer.send(topic, enriched_data)
#         on_send_success(record_metadata)

#     except Exception as e:
#         on_send_error(e)
#         raise
