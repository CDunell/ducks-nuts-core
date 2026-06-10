import pytest
from feature_factory.realtime.feature_validator import validate_features

def test_import_validate_features():
    assert callable(validate_features)
