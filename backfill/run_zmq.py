# backfill/run_zmq.py
"""
Entry point to start the ZMQ subscriber and dispatch ticks.
"""
import asyncio
import json
from .stream import ZMQSubscriber

def tick_handler(msg: bytes):
    """Decode and handle incoming tick message."""
    try:
        tick = json.loads(msg.decode())
    except Exception:
        tick = msg.decode()
    print(f"Received tick: {tick}")
    # TODO: send tick to feature processing pipeline

async def main():
    address = "tcp://127.0.0.1:5555"  # replace with your PUB socket address
    subscriber = ZMQSubscriber(address)
    await subscriber.run(tick_handler)

if __name__ == "__main__":
    asyncio.run(main())
