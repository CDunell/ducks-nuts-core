# backfill/tests/test_stream.py
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
    # allow SUB to connect
    await asyncio.sleep(0.1)
    # publish test message
    await pub.send(b'{"price":123.45,"qty":10}')
    # allow message to be received
    await asyncio.sleep(0.1)
    task.cancel()
    pub.close()
    ctx.term()

    assert received, "No message received by subscriber"
    assert received[0] == b'{"price":123.45,"qty":10}'
