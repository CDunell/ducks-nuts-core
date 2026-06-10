import pytest
from feature_factory.realtime.feature_registry import FeatureRegistry

def test_import_feature_registry():
    assert FeatureRegistry is not None
