import pytest
from datetime import datetime
from feature_factory.backfill.clients import BinanceClient

pytest_plugins = ["pytest_httpx"]


@pytest.mark.asyncio
async def test_fetch_ohlcv_single_page(httpx_mock):
    # mock a small klines response
    sample = [
        [1609459200000, "1", "2", "3", "4", "5", 1609459260000, "0", 0, "0", "0", "0"],
    ]
    httpx_mock.add_response(json=sample)

    client = BinanceClient()
    result = await client.fetch_ohlcv(
        "BTCUSDT",
        start_time=datetime(2021, 1, 1, 0, 0),
        end_time=datetime(2021, 1, 1, 0, 1),
    )
    assert result == sample
    await client.close()


@pytest.mark.asyncio
async def test_fetch_ohlcv_pagination(httpx_mock):
    # first page = full limit, second page = tail
    first = [[i, str(i), str(i), str(i), str(i), str(i), i + 999, "0", 0, "0", "0", "0"] for i in range(1000)]
    second = [
        [1609459800000, "a", "b", "c", "d", "e", 1609459860000, "0", 0, "0", "0", "0"]
    ]
    httpx_mock.add_response(json=first)
    httpx_mock.add_response(json=second)

    client = BinanceClient()
    data = await client.fetch_ohlcv(
        "BTCUSDT",
        start_time=datetime.fromtimestamp(0),
        end_time=datetime.fromtimestamp(10),
    )
    # should combine both pages
    assert len(data) == 1001
    assert data[-1] == second[0]
    await client.close()


@pytest.mark.asyncio
async def test_empty_response(httpx_mock):
    # no data at all
    httpx_mock.add_response(json=[])
    client = BinanceClient()
    data = await client.fetch_ohlcv(
        "BTCUSDT",
        start_time=datetime(2021, 1, 1),
        end_time=datetime(2021, 1, 1, 0, 1),
    )
    assert data == []
    await client.close()
