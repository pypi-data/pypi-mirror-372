import mm_print

from mm_btc.tx import decode_tx


def run(tx_hex: str, testnet: bool = False) -> None:
    res = decode_tx(tx_hex, testnet)
    mm_print.json(res)
