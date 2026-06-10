import duckdb
import time
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('FeatureMonitor')

class FeatureMonitor:
    def __init__(self, db_path="data/features.db"):
        self.db_path = db_path
    
    def get_stats(self):
        with duckdb.connect(self.db_path) as conn:
            stats = conn.execute("""
                SELECT 
                    COUNT(DISTINCT symbol) as symbol_count,
                    COUNT(DISTINCT feature_name) as feature_count,
                    MIN(timestamp) as earliest,
                    MAX(timestamp) as latest,
                    COUNT(*) as total_rows
                FROM features
            """).fetchone()
            
            queue_stats = conn.execute("""
                SELECT COUNT(*) as unprocessed 
                FROM raw_ticks 
                WHERE processed = FALSE
            """).fetchone()
            
            return {
                'symbols': stats[0],
                'features': stats[1],
                'time_range': f"{stats[2]} to {stats[3]}",
                'total_rows': stats[4],
                'unprocessed_ticks': queue_stats[0]
            }
    
    def run(self, interval=300):
        """Run monitoring loop"""
        logger.info("Starting feature store monitor")
        while True:
            stats = self.get_stats()
            logger.info(
                f"Feature Store Status:\n"
                f"- Symbols: {stats['symbols']}\n"
                f"- Features: {stats['features']}\n"
                f"- Time Range: {stats['time_range']}\n"
                f"- Total Rows: {stats['total_rows']:,}\n"
                f"- Unprocessed Ticks: {stats['unprocessed_ticks']}"
            )
            time.sleep(interval)

if __name__ == "__main__":
    monitor = FeatureMonitor()
    try:
        monitor.run()
    except KeyboardInterrupt:
        logger.info("Monitoring stopped")