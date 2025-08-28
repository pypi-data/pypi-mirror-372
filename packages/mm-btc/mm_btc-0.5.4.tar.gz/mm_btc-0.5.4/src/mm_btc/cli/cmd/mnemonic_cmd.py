from dataclasses import dataclass
from enum import Enum

import mm_print

from mm_btc.wallet import AddressType, derive_accounts, generate_mnemonic


class PrivateType(str, Enum):
    hex = "hex"
    wif = "wif"


@dataclass
class Args:
    mnemonic: str
    passphrase: str
    words: int
    limit: int
    hex: bool  # Print private key in hex format instead of WIF
    address_type: AddressType
    path: str
    testnet: bool


def run(args: Args) -> None:
    mnemonic = args.mnemonic or generate_mnemonic()
    passphrase = args.passphrase
    path = get_derivation_path_prefix(args.path, args.testnet)
    accounts = derive_accounts(mnemonic, passphrase, path, args.address_type, args.limit)

    mm_print.plain(f"{mnemonic}")
    if passphrase:
        mm_print.plain(f"{passphrase}")
    for acc in accounts:
        private = acc.private if args.hex else acc.wif
        mm_print.plain(f"{acc.path} {acc.address} {private}")


def get_derivation_path_prefix(path: str, testnet: bool) -> str:
    if path.startswith("m/"):
        return path
    coin = "1" if testnet else "0"
    if path == "bip44":
        return f"m/44'/{coin}'/0'/0"
    if path == "bip84":
        return f"m/84'/{coin}'/0'/0"

    raise ValueError("Invalid path")
