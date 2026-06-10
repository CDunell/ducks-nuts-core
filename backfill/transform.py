# backfill/transform.py

import pandas as pd
from typing import List, Any

def transform_ohlcv(raw: List[List[Any]]) -> pd.DataFrame:
    """
    Convert raw Binance kline lists into a clean DataFrame with:
    open_time, open, high, low, close, volume,
    close_time, quote_asset_volume, num_trades,
    taker_buy_base_asset_volume, taker_buy_quote_asset_volume.
    """
    # full Binance schema (we drop only the 'ignore' column)
    cols = [
        "open_time",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time",
        "quote_asset_volume",
        "num_trades",
        "taker_buy_base_asset_volume",
        "taker_buy_quote_asset_volume",
        "ignore",
    ]
    # build DataFrame
    df = pd.DataFrame(raw, columns=cols)

    # convert timestamps from milliseconds
    df["open_time"]  = pd.to_datetime(df["open_time"], unit="ms")
    df["close_time"] = pd.to_datetime(df["close_time"], unit="ms")

    # cast numeric fields
    numeric_cols = [
        "open",
        "high",
        "low",
        "close",
        "volume",
        "quote_asset_volume",
        "taker_buy_base_asset_volume",
        "taker_buy_quote_asset_volume",
    ]
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["num_trades"] = df["num_trades"].astype(int)

    # drop the unused column
    df = df.drop(columns=["ignore"])

    return df

# for backwards compatibility (if anything still calls transform_klines)
transform_klines = transform_ohlcv
