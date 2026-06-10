import os
import json
import redis

r = redis.Redis()
for i in range(5):
    message = {"symbol": "BTCUSDT", "price": 30000 + i, "volume": 0.5 + i}
    r.publish("market-signals", json.dumps(message))
    print(f"Sent: {message}")
