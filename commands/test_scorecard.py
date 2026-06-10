import pytest
from click.testing import CliRunner
from feature_factory.commands.scorecard import scorecard

@pytest.fixture
def runner():
    return CliRunner()

def test_scorecard_defaults(monkeypatch, runner):
    calls = {}
    def fake_generate_scorecard(input_db, report_path):
        calls.update(dict(input_db=input_db, report_path=report_path))

    monkeypatch.setattr(
        "feature_factory.commands.scorecard.generate_scorecard",
        fake_generate_scorecard,
    )

    result = runner.invoke(scorecard, [])
    assert result.exit_code == 0
    assert calls == {
        "input_db": "features.duckdb",
        "report_path": "scorecard.md",
    }
