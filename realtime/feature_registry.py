#!/usr/bin/env python3
# PATCHED
# Date: 2025-07-21
# Task: Patched log_performance to handle NaN/Infinity values for JSON serialization.
# Source: uploaded:feature_registry.py

import psycopg2
import psycopg2.extras
import json
import logging
import math

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('FeatureRegistry')

class FeatureRegistry:
    def __init__(self, db_params: dict):
        """
        Initializes the connection to the PostgreSQL database.
        
        Args:
            db_params (dict): Connection parameters for psycopg2.
        """
        try:
            self.conn = psycopg2.connect(**db_params)
            self.cursor = self.conn.cursor()
            self._init_db()
            logger.info("FeatureRegistry initialized and connected to PostgreSQL.")
        except psycopg2.OperationalError as e:
            logger.error(f"Could not connect to PostgreSQL database: {e}")
            raise

    def _init_db(self):
        """Initializes the database schema if it doesn't exist."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS features (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                description TEXT,
                category VARCHAR(255),
                code_logic TEXT NOT NULL,
                status VARCHAR(50) DEFAULT 'ideated',
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS feature_performance (
                id SERIAL PRIMARY KEY,
                feature_id INTEGER NOT NULL REFERENCES features(id) ON DELETE CASCADE,
                validation_date TIMESTAMPTZ DEFAULT NOW(),
                metrics JSONB
            );
        """)
        self.conn.commit()
        logger.info("Database tables 'features' and 'feature_performance' are ready.")

    def add_feature_idea(self, name: str, description: str, category: str, code_logic: str):
        """Adds a new feature to the registry with 'ideated' status."""
        sql = """
            INSERT INTO features (name, description, category, code_logic)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (name) DO NOTHING;
        """
        try:
            self.cursor.execute(sql, (name, description, category, code_logic))
            self.conn.commit()
            logger.info(f"Added/ignored feature idea: {name}")
        except Exception as e:
            logger.error(f"Failed to add feature idea '{name}': {e}")
            self.conn.rollback()

    def get_features_by_status(self, status: str) -> list:
        """Retrieves all features with a given status."""
        sql = "SELECT id, name, code_logic FROM features WHERE status = %s;"
        self.cursor.execute(sql, (status,))
        return self.cursor.fetchall()

    def update_feature_status(self, feature_id: int, new_status: str):
        """Updates the status of a specific feature."""
        sql = "UPDATE features SET status = %s WHERE id = %s;"
        try:
            self.cursor.execute(sql, (new_status, feature_id))
            self.conn.commit()
            logger.info(f"Updated feature {feature_id} status to '{new_status}'.")
        except Exception as e:
            logger.error(f"Failed to update status for feature {feature_id}: {e}")
            self.conn.rollback()

    def log_performance(self, feature_id: int, metrics: dict):
        """Logs a new performance record for a feature, handling non-finite numbers."""
        sql = "INSERT INTO feature_performance (feature_id, metrics) VALUES (%s, %s);"
        try:
            # Clean the metrics dict to ensure JSON compatibility (NaN/Infinity -> null)
            cleaned_metrics = {}
            for key, value in metrics.items():
                if isinstance(value, float) and not math.isfinite(value):
                    cleaned_metrics[key] = None
                else:
                    cleaned_metrics[key] = value
            
            metrics_json = json.dumps(cleaned_metrics)
            self.cursor.execute(sql, (feature_id, metrics_json))
            self.conn.commit()
            logger.info(f"Logged performance for feature {feature_id}.")
        except Exception as e:
            logger.error(f"Failed to log performance for feature {feature_id}: {e}")
            self.conn.rollback()
            
    def get_live_features_code(self) -> list:
        """Retrieves the name and code logic for all 'live' features."""
        sql = "SELECT name, code_logic FROM features WHERE status = 'live' ORDER BY name;"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def close(self):
        """Closes the database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("PostgreSQL connection closed.")

if __name__ == '__main__':
    # Example usage:
    db_connection_params = {
        "dbname": "cta_db",
        "user": "postgre",
        "password": "a",
        "host": "localhost", # Assuming default host
        "port": "5432"      # Assuming default port
    }

    try:
        registry = FeatureRegistry(db_params=db_connection_params)
        print("FeatureRegistry initialized successfully.")
        
        # Example of adding a feature
        registry.add_feature_idea(
            name='example_momentum',
            description='A simple 5-day momentum feature.',
            category='momentum',
            code_logic="df['example_momentum'] = df['close'].pct_change(5)"
        )
        
        # Example of retrieving features
        ideated_features = registry.get_features_by_status('ideated')
        print(f"Found {len(ideated_features)} ideated features.")

        registry.close()

    except Exception as e:
        print(f"An error occurred during the example run: {e}")