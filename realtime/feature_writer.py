import zmq
import pandas as pd
import numpy as np
from collections import deque
from feature_factory.deployed_features import apply_all_features
import logging
from duckdb_feature_store import DuckDBFeatureStore

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("FeatureWriter")

class FeatureWriter:
    def __init__(self, lmdb_path="data/features", buffer_size=50, symbol="BTCUSDT"):
        self.context = zmq.Context()
        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.connect("tcp://localhost:5555")
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, "")

        self.symbol = symbol
        self.buffer = deque(maxlen=buffer_size)
        self.feature_store = DuckDBFeatureStore()

    def run(self):
        logger.info("🟢 FeatureWriter started")
        while True:
            try:
                tick = self.subscriber.recv_json()
                if tick["symbol"] != self.symbol:
                    continue
                
                # Store raw tick
                self.feature_store.store_raw_tick(tick)
                
                # Add to processing buffer
                self.buffer.append(tick)

                if len(self.buffer) >= self.buffer.maxlen:
                    self.process()
            except Exception as e:
                logger.error(f"Tick processing error: {str(e)}")
                time.sleep(1)

    def process(self):
        try:
            df = pd.DataFrame(self.buffer)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Apply feature computation
            enriched = apply_all_features(df.copy())
            
            # Store features
            self.feature_store.store_features(enriched)
            logger.info(f"✅ Processed {len(df)} ticks for {self.symbol}")

        except Exception as e:
            logger.error(f"Feature computation failed: {str(e)}")

if __name__ == "__main__":
    writer = FeatureWriter()
    try:
        writer.run()
    except KeyboardInterrupt:
        writer.feature_store.close()
        logger.info("FeatureWriter shutdown complete")