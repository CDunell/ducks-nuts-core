# backfill/tests/test_stream.py
# ⚠️ PATCHED: 2025-07-24
# Task: Prevent hanging test by awaiting cancelled subscriber task
# Source file ID: file-UUJXERfZ7j3Fhp1zn5kuKk
# SHA256: 6b616f498c2c7355e3be6d719c7461797a4a05753e42bda53e8db3d8ff58d229

import pytest
import asyncio
import zmq
import zmq.asyncio
from feature_factory.backfill.stream import ZMQSubscriber

@pytest.mark.asyncio
async def test_stream_receives_one_tick():
    ctx = zmq.asyncio.Context.instance()
    pub = ctx.socket(zmq.PUB)
    port = pub.bind_to_random_port("tcp://127.0.0.1")
    subscriber = ZMQSubscriber(f"tcp://127.0.0.1:{port}")

    received = []

    def handler(msg):
        received.append(msg)

    task = asyncio.create_task(subscriber.run(handler))
    await asyncio.sleep(0.1)
    await pub.send(b'{"price":123.45,"qty":10}')
    await asyncio.sleep(0.1)

    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    pub.close()
    ctx.term()

    assert received, "No message received by subscriber"
    assert received[0] == b'{"price":123.45,"qty":10}'
