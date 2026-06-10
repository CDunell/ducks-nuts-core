import os
from pathlib import Path
import pytest
from typer.testing import CliRunner

from feature_factory.backfill.cli import app

runner = CliRunner()

@pytest.fixture
def db_file(tmp_path):
    return str(tmp_path / "test.duckdb")

def test_start_and_status(db_file):
    # start a job
    result = runner.invoke(
        app,
        [
            "start",
            "--exchange", "binance",
            "--symbol", "BTCUSDT",
            "--start", "2025-01-01T00:00:00",
            "--end", "2025-01-02T00:00:00",
            "--db-path", db_file,
        ],
    )
    assert result.exit_code == 0
    assert result.stdout.startswith("Created job ")
    job_id = result.stdout.strip().split()[-1]

    # check its status
    result2 = runner.invoke(
        app,
        ["status", job_id, "--db-path", db_file],
    )
    assert result2.exit_code == 0
    assert f"Job {job_id}: PENDING" in result2.stdout

def test_status_not_found(db_file):
    result = runner.invoke(
        app,
        ["status", "nonexistent-id", "--db-path", db_file],
    )
    assert result.exit_code != 0
    assert "Job nonexistent-id not found" in result.stdout
