# duckdb_feature_store.py
# PATCHED
# Patch date: 2025-07-22
# Task: Implement missing _initialize_optimized_connection method
# Source file ID: file-duckdb_feature_store.py
# STRICT_PATCH.md enforced from: file-Fr1qZs17TppynEb5FZwukq

import duckdb
import pandas as pd
import logging
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import threading
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('DuckDBFeatureStore')

class DuckDBFeatureStore:
    def __init__(self, db_path="data/features.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.write_queue = Queue()
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.conn = self._initialize_optimized_connection()
        self._init_db()
        self._writer_running = True
        self._writer_thread = threading.Thread(target=self._writer, daemon=True)
        self._writer_thread.start()

    def _initialize_optimized_connection(self):
        """Initialize connection with DuckDB performance optimizations"""
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                conn = duckdb.connect(str(self.db_path))
                
                # DuckDB-specific performance optimizations
                conn.execute("SET threads TO 4")  # Use 4 CPU threads
                conn.execute("SET memory_limit='8GB'")  # Increase memory limit
                
                logger.info("Database connection established with optimizations")
                return conn
                
            except Exception as e:
                logger.error(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt == max_attempts - 1:
                    logger.critical("Failed to establish database connection")
                    raise
                time.sleep(1)
                self._recover_database()

    def _recover_database(self):
        """Handle database corruption by resetting"""
        try:
            if self.db_path.exists():
                logger.warning(f"Removing corrupted database: {self.db_path}")
                if hasattr(self, 'conn') and self.conn:
                    self.conn.close()
                os.remove(self.db_path)
        except Exception as e:
            logger.error(f"Database recovery failed: {e}")
            raise

    def _writer(self):
        while self._writer_running:
            batch = []
            while not self.write_queue.empty():
                batch.append(self.write_queue.get())
            
            if batch:
                try:
                    self.conn.begin()
                    try:
                        with self.conn.cursor() as cursor:
                            for record_batch in batch:
                                cursor.executemany("""
                                    INSERT INTO features 
                                    (timestamp, symbol, feature_name, feature_value)
                                    VALUES (?, ?, ?, ?)
                                    ON CONFLICT (symbol, timestamp, feature_name) 
                                    DO UPDATE SET feature_value = EXCLUDED.feature_value
                                """, record_batch)
                        self.conn.commit()
                    except Exception as e:
                        self.conn.rollback()
                        raise
                except Exception as e:
                    logger.error(f"Batch write failed: {e}")
                    for item in batch:
                        self.write_queue.put(item)
                    time.sleep(1)
            else:
                time.sleep(0.1)

    def close(self):
        """Clean up resources"""
        logger.info("Shutting down writer thread...")
        self._writer_running = False
        self._writer_thread.join(timeout=5.0)
        self.executor.shutdown(wait=True)
        self.conn.close()
        logger.info("Feature store connection closed")

    def _init_db(self):
        """Initialize database schema with optimized settings"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS features (
                timestamp TIMESTAMP,
                symbol VARCHAR,
                feature_name VARCHAR,
                feature_value FLOAT,
                computation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (symbol, timestamp, feature_name)
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS raw_ticks (
                timestamp TIMESTAMP,
                symbol VARCHAR,
                open FLOAT,
                high FLOAT,
                low FLOAT,
                close FLOAT,
                volume FLOAT,
                processed BOOLEAN DEFAULT FALSE,
                PRIMARY KEY (symbol, timestamp))
        """)
        
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_features_symbol ON features(symbol)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_features_timestamp ON features(timestamp)")
        
        logger.info("Initialized optimized DuckDB feature store")

    def store_raw_tick(self, tick_data: dict):
        """Store raw tick data with conflict handling"""
        try:
            self.conn.execute("""
                INSERT INTO raw_ticks 
                (timestamp, symbol, open, high, low, close, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (symbol, timestamp) DO NOTHING
            """, [
                tick_data['timestamp'],
                tick_data['symbol'],
                float(tick_data['open']),
                float(tick_data['high']),
                float(tick_data['low']),
                float(tick_data['close']),
                float(tick_data['volume'])
            ])
        except Exception as e:
            logger.error(f"Failed to store tick: {e}")
            raise

    def store_features(self, features_df: pd.DataFrame):
        """Convert DataFrame to feature records"""
        if features_df.empty:
            return

        records = []
        for _, row in features_df.iterrows():
            timestamp = pd.to_datetime(row['timestamp'])
            symbol = row['symbol']
            for col in features_df.columns:
                if col not in ['timestamp', 'symbol'] and pd.notna(row[col]):
                    records.append((
                        timestamp,
                        symbol,
                        col,
                        float(row[col])
                    ))
        
        for chunk in [records[i:i+1000] for i in range(0, len(records), 1000)]:
            self.write_queue.put(chunk)
        logger.debug(f"Queued {len(records)} feature records")

    def get_tick_count(self, symbol: str) -> int:
        """Get count of ticks for a symbol"""
        return self.conn.execute(
            "SELECT COUNT(*) FROM raw_ticks WHERE symbol=?", 
            [symbol]
        ).fetchone()[0]

if __name__ == "__main__":
    store = DuckDBFeatureStore()
    try:
        test_df = pd.DataFrame({
            'timestamp': [pd.Timestamp.now()],
            'symbol': ['TEST'],
            'feature1': [1.23],
            'feature2': [4.56]
        })
        store.store_features(test_df)
        print("Test completed successfully")
    finally:
        store.close()