# feature_factory/backfill/healthcheck.py
import aiohttp
import duckdb
from pathlib import Path

async def test_binance_connection():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get("https://api.binance.com/api/v3/ping") as resp:
                return resp.status == 200
        except:
            return False

def test_duckdb_connection():
    try:
        conn = duckdb.connect()
        conn.execute("SELECT 1")
        return True
    except:
        return False