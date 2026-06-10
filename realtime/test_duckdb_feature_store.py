import pytest
from feature_factory.realtime.duckdb_feature_store import DuckDBFeatureStore

def test_import_duckdb_feature_store():
    assert DuckDBFeatureStore is not None
