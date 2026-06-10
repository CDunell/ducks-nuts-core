# backfill/tests/test_transform.py

import pandas as pd
import pytest
from feature_factory.backfill.transform import transform_ohlcv

def test_transform_full_schema():
    # raw kline row with all Binance fields (we drop only "ignore")
    raw = [[
        1609459200000, "1", "2", "3", "4", "5",
        1609459260000, "6", 7, "8", "9", "ignore"
    ]]
    df = transform_ohlcv(raw)
    expected = [
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "num_trades",
        "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume"
    ]
    assert list(df.columns) == expected

    row = df.iloc[0]
    assert row.open_time == pd.to_datetime(1609459200000, unit="ms")
    assert row.open == 1.0
    assert row.high == 2.0
    assert row.low == 3.0
    assert row.close == 4.0
    assert row.volume == 5.0
    assert row.close_time == pd.to_datetime(1609459260000, unit="ms")
    assert row.quote_asset_volume == 6.0
    assert row.num_trades == 7
    assert row.taker_buy_base_asset_volume == 8.0
    assert row.taker_buy_quote_asset_volume == 9.0
