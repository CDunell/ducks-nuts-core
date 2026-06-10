#!/usr/bin/env python3
"""
Realtime Feature Lifecycle Runner
Publishes enriched feature vectors to DuckDB and CTA via bridge adapter.
"""
import os
import logging
import click

from feature_factory.realtime.tick_processor_zmq import ZMQSubscriber
from feature_factory.realtime.rt_generator import generate_features
from feature_factory.realtime.feature_validator import validate_features
from feature_factory.realtime.duckdb_feature_store import DuckDBFeatureStore
from feature_factory.realtime.bridge_adapter import BridgeAdapter

logger = logging.getLogger(__name__)

@click.command()
@click.option('--db-path', '-d', default='./data/features_sample.duckdb', help='DuckDB path')
@click.option('--zmq-url', '-z', default=lambda: os.getenv('ZMQ_URL'), help='ZMQ URL for enriched feature publish')
def main(db_path, zmq_url):
    """Run the real-time feature pipeline."""
    # Initialize components
    store = DuckDBFeatureStore(db_path=db_path)
    adapter = BridgeAdapter(zmq_url=zmq_url)
    subscriber = ZMQSubscriber(os.getenv('ZMQ_URL'))

    # Handler for each incoming tick
    def handle_tick(tick):
        features = generate_features(tick)
        if validate_features(features):
            store.write(features)
            try:
                adapter.publish(features)
            except Exception as e:
                logger.error(f"Bridge publish failed: {e}")

    # Start subscriber loop
    subscriber.run(handle_tick)

if __name__ == '__main__':
    logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))
    main()
