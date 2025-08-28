import mm_print

from mm_btc.blockstream import BlockstreamClient
from mm_btc.wallet import is_testnet_address


async def run(address: str) -> None:
    client = BlockstreamClient(testnet=is_testnet_address(address))
    res = await client.get_utxo(address)
    mm_print.json(res.value_or_error())
