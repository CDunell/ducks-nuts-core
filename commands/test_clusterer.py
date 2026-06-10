import pytest
from click.testing import CliRunner
from feature_factory.commands.clusterer import clusterer

@pytest.fixture
def runner():
    return CliRunner()

def test_clusterer_defaults(monkeypatch, runner):
    calls = {}
    def fake_run_clustering(input_db, output, method):
        calls.update(dict(input_db=input_db, output=output, method=method))

    monkeypatch.setattr(
        "feature_factory.commands.clusterer.run_clustering",
        fake_run_clustering,
    )

    result = runner.invoke(clusterer, [])
    assert result.exit_code == 0
    assert calls == {
        "input_db": "features.duckdb",
        "output": "clusters.csv",
        "method": "hdbscan",
    }
