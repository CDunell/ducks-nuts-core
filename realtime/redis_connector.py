# ==============================================
# redis_connector.py
# Patch Date: 2025-07-25
# Task: Replace KafkaConnector with RedisConnector for local dev
# ==============================================

import asyncio
import json
import os
import redis.asyncio as redis

class RedisConnector:
    def __init__(self, channel="market-signals"):
        self.channel = channel
        self.sub = None
        self.pub = redis.Redis()
        self._running = False

    async def start(self, message_handler):
        self.sub = self.pub.pubsub()
        await self.sub.subscribe(self.channel)
        self._running = True
        while self._running:
            message = await self.sub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message:
                class FakeMsg:
                    def __init__(self, value): self.value = value
                await message_handler(FakeMsg(message["data"]))

    async def send(self, message: bytes):
        await self.pub.publish(self.channel, message)

    async def stop(self):
        self._running = False
        if self.sub:
            await self.sub.unsubscribe(self.channel)
            await self.sub.close()
