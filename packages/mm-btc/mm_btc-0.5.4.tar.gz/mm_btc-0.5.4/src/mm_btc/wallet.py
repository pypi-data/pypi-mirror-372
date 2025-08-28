from dataclasses import dataclass
from enum import Enum, unique

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin
from hdwallet.derivations import CustomDerivation
from hdwallet.hds import BIP32HD
from hdwallet.mnemonics import BIP39Mnemonic
from mnemonic import Mnemonic

BIP44_MAINNET_PATH = "m/44'/0'/0'/0"
BIP44_TESTNET_PATH = "m/44'/1'/0'/0"
BIP84_MAINNET_PATH = "m/84'/0'/0'/0"
BIP84_TESTNET_PATH = "m/84'/1'/0'/0"


@dataclass
class Account:
    address: str
    private: str
    wif: str
    path: str


@unique
class AddressType(str, Enum):
    P2PKH = "P2PKH"  # Pay to Public Key Hash
    P2SH = "P2SH"  # Pay to Script Hash
    P2TR = "P2TR"  # Taproot
    P2WPKH = "P2WPKH"  # Native SegWit
    P2WPKH_IN_P2SH = "P2WPKH-In-P2SH"
    P2WSH = "P2WSH"  # Native SegWit
    P2WSH_IN_P2SH = "P2WSH-In-P2SH"


def generate_mnemonic(language: str = "english", words: int = 12) -> str:
    return Mnemonic(language).generate(strength=mnemonic_words_to_strenght(words))


def derive_accounts(mnemonic: str, passphrase: str, path_prefix: str, address_type: AddressType, limit: int) -> list[Account]:
    coin = Bitcoin
    if path_prefix.startswith(("m/84'/1'", "m/44'/1'")):
        network = coin.NETWORKS.TESTNET
    elif path_prefix.startswith(("m/84'/0'", "m/44'/0'")):
        network = coin.NETWORKS.MAINNET
    else:
        raise ValueError("Invalid path")

    wallet = HDWallet(cryptocurrency=coin, network=network, hd=BIP32HD, passphrase=passphrase).from_mnemonic(
        BIP39Mnemonic(mnemonic)
    )
    wallet.clean_derivation()

    accounts = []
    for index_path in range(limit):
        wallet.clean_derivation()
        path = f"{path_prefix}/{index_path}"
        w = wallet.from_derivation(derivation=CustomDerivation(path=path))
        accounts.append(Account(address=w.address(address_type), private=w.private_key(), wif=w.wif(), path=path))
        w.clean_derivation()

    return accounts


def mnemonic_words_to_strenght(words: int) -> int:
    if words == 12:
        return 128
    if words == 15:
        return 160
    if words == 18:
        return 192
    if words == 21:
        return 224
    if words == 24:
        return 256

    raise ValueError("Invalid words")


def is_testnet_address(address: str) -> bool:
    return address.startswith(("m", "n", "tb1"))
