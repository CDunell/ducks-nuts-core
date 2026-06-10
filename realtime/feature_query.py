import duckdb
import pandas as pd
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('FeatureQuery')

class FeatureQuery:
    def __init__(self, db_path="data/features.db"):
        self.conn = duckdb.connect(db_path)
    
    def get_features(self, symbol: str, start_date: datetime = None, end_date: datetime = None):
        """Query features for a specific symbol and time range"""
        query = "SELECT * FROM features WHERE symbol = ?"
        params = [symbol]
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        
        query += " ORDER BY timestamp DESC"
        
        try:
            return self.conn.execute(query, params).fetchdf()
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return pd.DataFrame()
    
    def get_feature_stats(self, feature_name: str):
        """Get statistics for a specific feature"""
        return self.conn.execute("""
            SELECT 
                symbol,
                COUNT(*) as count,
                AVG(feature_value) as mean,
                STDDEV(feature_value) as stddev,
                MIN(feature_value) as min,
                MAX(feature_value) as max
            FROM features
            WHERE feature_name = ?
            GROUP BY symbol
        """, [feature_name]).fetchdf()
    
    def close(self):
        self.conn.close()

if __name__ == "__main__":
    query = FeatureQuery()
    try:
        # Example queries
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=1)
        
        print("Latest BTC features:")
        print(query.get_features("BTCUSDT", limit=5))
        
        print("\nBTC features from last 24 hours:")
        print(query.get_features("BTCUSDT", start_date=start_date, end_date=end_date))
        
        print("\nFeature statistics for RSI_14:")
        print(query.get_feature_stats("RSI_14"))
        
    finally:
        query.close()