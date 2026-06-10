import pytest
from feature_factory.realtime.rt_generator import generate_features

def test_import_generate_features():
    assert callable(generate_features)
