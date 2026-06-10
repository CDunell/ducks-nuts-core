
import asyncio
import os
from aiokafka import AIOKafkaProducer

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_CONSUMER_TOPIC = os.getenv("KAFKA_CONSUMER_TOPIC", "test_topic")

async def send_messages():
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    await producer.start()
    try:
        for i in range(5):
            value = f"test-message-{i}".encode("utf-8")
            await producer.send_and_wait(KAFKA_CONSUMER_TOPIC, value=value)
            print(f"Sent: {value}")
    finally:
        await producer.stop()

if __name__ == "__main__":
    asyncio.run(send_messages())
