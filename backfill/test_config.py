import os
import pytest
from feature_factory.backfill.config import Settings

@pytest.fixture(autouse=True)
def env_file(tmp_path, monkeypatch):
    # create a temporary .env in working dir
    f = tmp_path / ".env"
    f.write_text(
        "DATABASE_PATH=test.db\n"
        "BINANCE_API_KEY=key123\n"
        "BINANCE_API_SECRET=secret123\n"
    )
    monkeypatch.chdir(tmp_path)

def test_settings_load():
    s = Settings()
    assert s.DATABASE_PATH == "test.db"
    assert s.BINANCE_API_KEY == "key123"
    assert s.BINANCE_API_SECRET == "secret123"
