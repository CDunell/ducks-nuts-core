# 🔒 PATCHED: 2025-07-25
# Task: Use pydantic_settings for BaseSettings to satisfy Pydantic v2 separation
# Source file: src/feature_factory/backfill/config.py (file-SQcMkRCXFyRshWogKXmDpw)

# backfill/config.py

# Pydantic v2.11 migration: BaseSettings moved to pydantic-settings
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # sensible defaults for local dev / tests
    DATABASE_PATH: str = "sqlite:///./backfill.db"
    BINANCE_API_KEY: str = ""
    BINANCE_API_SECRET: str = ""
    # TESTING-mode credentials
    BINANCE_TESTNET_API_KEY: str = ""
    BINANCE_TESTNET_API_SECRET: str = ""
    # when True, skips the FK on chunks table for testing
    TESTING: bool = False
    # optional: logging level
    LOG_LEVEL: str = "INFO"

    class Config:
        # load overrides from a .env file at project root
        env_file = ".env"
        env_file_encoding = "utf-8"
        # ignore any extra environment variables not defined above
        extra = "ignore"

# single Settings instance, picks up real env-vars or .env overrides
settings = Settings()
