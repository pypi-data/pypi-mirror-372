from bitcoinlib.transactions import Transaction


def decode_tx(tx_hex: str, testnet: bool = False) -> dict[str, object]:
    return Transaction.parse(tx_hex, network="testnet" if testnet else "mainnet").as_dict()  # type: ignore[no-any-return]
