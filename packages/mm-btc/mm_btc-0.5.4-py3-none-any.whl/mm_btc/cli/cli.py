import asyncio
import importlib.metadata
from pathlib import Path
from typing import Annotated

import mm_print
import typer

from mm_btc.wallet import AddressType

from .cmd import address_cmd, create_tx_cmd, decode_tx_cmd, mnemonic_cmd, utxo_cmd

app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False, add_completion=False)


@app.command("mnemonic")
@app.command(name="m", hidden=True)
def mnemonic_command(  # nosec B107:hardcoded_password_default
    mnemonic: Annotated[str, typer.Option("--mnemonic", "-m", help="")] = "",
    passphrase: Annotated[str, typer.Option("--passphrase", "-p")] = "",
    path: Annotated[str, typer.Option("--path", help="Derivation path. Examples: bip44, bip88, m/44'/0'/0'/0")] = "bip44",
    address_type: Annotated[AddressType, typer.Option("--address-type", "-a", help="Bitcoin address type")] = AddressType.P2WPKH,
    hex_: Annotated[bool, typer.Option("--hex", help="Print private key in hex format instead of WIF")] = False,
    words: int = typer.Option(12, "--words", "-w", help="Number of mnemonic words"),
    limit: int = typer.Option(10, "--limit", "-l"),
    testnet: bool = typer.Option(False, "--testnet", "-t", help="Testnet network"),
) -> None:
    """Generate keys based on a mnemonic"""
    mnemonic_cmd.run(
        mnemonic_cmd.Args(
            mnemonic=mnemonic,
            passphrase=passphrase,
            words=words,
            limit=limit,
            path=path,
            address_type=address_type,
            hex=hex_,
            testnet=testnet,
        )
    )


@app.command(name="address")
@app.command(name="a", hidden=True)
def address_command(address: str) -> None:
    """Get address info from Blockstream API"""
    asyncio.run(address_cmd.run(address))


@app.command("create-tx")
def create_tx_command(config_path: Annotated[Path, typer.Argument(exists=True)]) -> None:
    """Create a transaction"""
    create_tx_cmd.run(config_path)


@app.command("decode-tx")
def decode_tx_command(tx_hex: str, testnet: Annotated[bool, typer.Option("--testnet", "-t")] = False) -> None:
    """Decode a transaction"""
    decode_tx_cmd.run(tx_hex, testnet)


@app.command("utxo")
def utxo_command(address: str) -> None:
    """Get UTXOs from Blockstream API"""
    asyncio.run(utxo_cmd.run(address))


def version_callback(value: bool) -> None:
    if value:
        mm_print.plain(f"mm-btc: v{importlib.metadata.version('mm-btc')}")
        raise typer.Exit


@app.callback()
def main(_version: bool = typer.Option(None, "--version", callback=version_callback, is_eager=True)) -> None:
    pass


if __name__ == "__main_":
    app()
