import asyncio
import zmq
import zmq.asyncio

class ZMQSubscriber:
    def __init__(self, address: str, topic: bytes = b""):
        """
        Initializes a ZeroMQ SUB socket.
        :param address: e.g. "tcp://127.0.0.1:5555"
        :param topic: topic filter as bytes (empty for all messages)
        """
        self.ctx = zmq.asyncio.Context.instance()
        self.socket = self.ctx.socket(zmq.SUB)
        self.socket.connect(address)
        # Subscribe to the given topic (empty subscribes to all)
        self.socket.setsockopt(zmq.SUBSCRIBE, topic)

    async def listen(self):
        """
        Async generator yielding incoming raw messages.
        """
        while True:
            msg = await self.socket.recv()
            yield msg

    async def run(self, handler):
        """
        Continuously receives messages and dispatches to handler(msg).
        :param handler: a callable that accepts a bytes message
        """
        try:
            async for msg in self.listen():
                handler(msg)
        except asyncio.CancelledError:
            # Allow the run task to be cancelled cleanly
            pass
