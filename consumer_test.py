
import asyncio
from realtime.run_connector import main as run_connector

if __name__ == "__main__":
    asyncio.run(run_connector(run_seconds=10))
