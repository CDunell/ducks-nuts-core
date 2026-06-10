# ==============================================
# Patch Date: 2025-07-25
# Task: Redis-based test_connector.ps1 (fix heredoc)
# ==============================================

$ErrorActionPreference = "Stop"

# Step 1: Set PYTHONPATH
$env:PYTHONPATH = ".."

# Step 2: Generate temporary Python producer script using Redis
$producerScript = @"
import os
import json
import redis

r = redis.Redis()
for i in range(5):
    message = {"symbol": "BTCUSDT", "price": 30000 + i, "volume": 0.5 + i}
    r.publish("market-signals", json.dumps(message))
    print(f"Sent: {message}")
"@

Set-Content -Path "temp_produce.py" -Value $producerScript -Encoding UTF8

# Step 3: Generate temporary Python consumer script to run connector
$consumerScript = @"
import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=".env")

import asyncio
from realtime.run_connector import main

asyncio.run(main())
"@

Set-Content -Path "temp_consume.py" -Value $consumerScript -Encoding UTF8

# Step 4: Run the producer script
Write-Host "Publishing 5 test messages..."
python temp_produce.py

# Step 5: Run the consumer script
Write-Host "Running connector..."
python temp_consume.py

# Step 6: Query DuckDB to confirm rows were inserted
Write-Host "Checking DuckDB output..."
$checkScript = @"
import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=".env")

import duckdb
db_path = os.getenv("DUCKDB_PATH")
table = os.getenv("FEATURE_TABLE", "feature_snapshots")
con = duckdb.connect(database=db_path)
try:
    result = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
    print("Rows in table:", result[0])
except Exception as e:
    print("DuckDB query failed:", e)
"@

Set-Content -Path "temp_check.py" -Value $checkScript -Encoding UTF8
python temp_check.py

Write-Host "Temp scripts preserved."
