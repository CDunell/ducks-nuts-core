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
