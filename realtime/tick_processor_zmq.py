
class ZMQSubscriber:
    """Stub ZMQSubscriber for realtime tests"""
    def __init__(self, zmq_url: str):
        import zmq.asyncio
        self.ctx = zmq.asyncio.Context.instance()
        self.socket = self.ctx.socket(zmq.SUB)
        self.socket.connect(zmq_url)
        self.socket.setsockopt_string(zmq.SUBSCRIBE, '')

    async def run(self, handler):
        while True:
            msg = await self.socket.recv()
            await handler(msg)


#!/usr/bin/env python3
# PATCHED
# Date: 2025-07-21
# Task: Refactored to subscribe to top 10 coins by volume via a combined stream.
# Source: uploaded:tick_processor_zmq.py

import duckdb
import zmq
import psutil
import time
import json
import logging
import websocket
import requests
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('DataIngest')

def get_top_10_usdt_pairs():
    """Fetches the top 10 trading pairs against USDT by 24h quote volume."""
    try:
        url = "https://api.binance.com/api/v3/ticker/24hr"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Filter for pairs ending with USDT and sort by quote volume
        usdt_pairs = [p for p in data if p['symbol'].endswith('USDT')]
        sorted_pairs = sorted(usdt_pairs, key=lambda x: float(x['quoteVolume']), reverse=True)
        
        top_10 = [p['symbol'].lower() for p in sorted_pairs[:10]]
        return top_10
    except requests.exceptions.RequestException as e:
        logger.error(f"Could not fetch top symbols from Binance API: {e}")
        # Fallback to a default list if API fails
        return ["btcusdt", "ethusdt", "solusdt", "xrpusdt", "hypeusdt", "adausdt", "shibusdt", "avaxusdt", "linkusdt", "dotusdt"]


class BinanceWebsocketClient:
    def __init__(self, url: str, processor, symbols: list):
        self.ws_url = url
        self.processor = processor
        self.symbols = symbols
        self.ws_app = websocket.WebSocketApp(
            self.ws_url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )

    def _on_open(self, ws):
        streams = [f"{symbol}@kline_1m" for symbol in self.symbols]
        logger.info(f"WebSocket opened. Subscribing to {len(streams)} streams...")
        subscribe_message = {
            "method": "SUBSCRIBE",
            "params": streams,
            "id": 1
        }
        ws.send(json.dumps(subscribe_message))

    def _on_message(self, ws, message):
        try:
            payload = json.loads(message)
            # Handle combined stream format: {"stream": "...", "data": {...}}
            if 'stream' not in payload or 'data' not in payload:
                return
            
            data = payload['data']
            if 'e' not in data or data['e'] != 'kline':
                return
            
            kline = data['k']
            # Process only closed k-lines
            if kline['x']:
                tick = {
                    "timestamp": pd.to_datetime(kline['t'], unit='ms').isoformat(),
                    "symbol": kline['s'],
                    "open": float(kline['o']),
                    "high": float(kline['h']),
                    "low": float(kline['l']),
                    "close": float(kline['c']),
                    "volume": float(kline['v'])
                }
                self.processor.process_tick(tick)
        except Exception as e:
            logger.error(f"Error processing message: {e}\nMessage: {message}")

    def _on_error(self, ws, error):
        logger.error(f"WebSocket Error: {error}")

    def _on_close(self, ws, close_status_code, close_msg):
        logger.warning(f"WebSocket connection closed: {close_msg} ({close_status_code})")

    def run(self):
        logger.info("Starting WebSocket client...")
        self.ws_app.run_forever()


class TickProcessor:
    def __init__(self, duckdb_path="data/tick_store.db"):
        self.context = zmq.Context()
        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.bind("tcp://*:5555")
        Path(duckdb_path).parent.mkdir(parents=True, exist_ok=True)
        self.db = duckdb.connect(duckdb_path)
        self._init_db()
        logger.info(f"Initialized | DuckDB: {duckdb_path}")

    def _init_db(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS ticks (
                timestamp TIMESTAMP, symbol VARCHAR, open FLOAT, 
                high FLOAT, low FLOAT, close FLOAT, volume FLOAT
            )
        """)
        logger.info("DuckDB 'ticks' table initialized.")

    def process_tick(self, tick: dict):
        self.publisher.send_json(tick)
        try:
            self.db.execute("""
                INSERT INTO ticks VALUES (?,?,?,?,?,?,?)
            """, list(tick.values()))
        except duckdb.ConstraintException:
            logger.warning(f"Duplicate tick ignored for timestamp {tick['timestamp']}")
        
        if psutil.virtual_memory().percent > 75:
            self._flush_cold_data()

    def _flush_cold_data(self):
        # ... (This function remains unchanged)
        pass

if __name__ == "__main__":
    load_dotenv()
    
    ws_url = os.getenv("BINANCE_WS_URL")
    if not ws_url:
        raise ValueError("BINANCE_WS_URL not set in environment or .env file")

    try:
        top_10_symbols = get_top_10_usdt_pairs()
        logger.info(f"Tracking top 10 symbols by volume: {top_10_symbols}")
        
        processor = TickProcessor()
        ws_client = BinanceWebsocketClient(url=ws_url, processor=processor, symbols=top_10_symbols)
        ws_client.run()
        
    except KeyboardInterrupt:
        logger.info("Shutting down...")