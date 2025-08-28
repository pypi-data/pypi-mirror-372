import pytest

from mm_btc import blockstream
from mm_btc.blockstream import BlockstreamClient

pytestmark = pytest.mark.asyncio


async def test_get_address(binance_address, proxies):
    client = BlockstreamClient(proxies=proxies, timeout=5, attempts=5)

    # non-empty address
    res = await client.get_address(binance_address)
    assert res.unwrap().chain_stats.tx_count > 800

    # empty address
    res = await client.get_address("bc1pa48c294qk7yd7sc8y0wxydc3a2frv5j83e65rvm48v3ej098s5zs8kvh6d")
    assert res.unwrap().chain_stats.tx_count == 0

    # invalid address
    res = await client.get_address("bc1pa48c294qk7yd7sc8y0wxydc3a2frv5j83e65rvm48v3ej098s5zs8kvh5d")
    assert res.unwrap_err() == blockstream.ERROR_400_BAD_REQUEST

    # invalid network
    res = await client.get_address("mqkwWDWdgXhYunfoKvQfYyydwB5vdma3cK")
    assert res.unwrap_err() == blockstream.ERROR_400_BAD_REQUEST


async def test_get_confirmed_balance(binance_address, proxies):
    client = BlockstreamClient(proxies=proxies)
    res = await client.get_confirmed_balance(binance_address)
    assert res.unwrap() > 0
