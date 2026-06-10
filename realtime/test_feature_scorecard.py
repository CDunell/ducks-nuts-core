import pytest
from feature_factory.realtime.feature_scorecard import FeatureScorecard

def test_import_feature_scorecard():
    assert FeatureScorecard is not None
