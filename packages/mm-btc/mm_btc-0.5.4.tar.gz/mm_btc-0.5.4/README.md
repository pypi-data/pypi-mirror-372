# mm-btc

A Python library and CLI tool for Bitcoin operations, designed for developers who need to work with Bitcoin wallets, transactions, and blockchain data.

⚠️ **This project is under active development. New features and breaking changes may be introduced.**




## Library Usage

### Working with Mnemonics and Wallets

```python
from mm_btc.wallet import generate_mnemonic, derive_accounts, AddressType

# Generate a new mnemonic
mnemonic = generate_mnemonic(words=12)
print(f"Mnemonic: {mnemonic}")

# Derive accounts from mnemonic
accounts = derive_accounts(
    mnemonic=mnemonic,
    passphrase="",
    path_prefix="m/84'/0'/0'/0",  # BIP84 mainnet
    address_type=AddressType.P2WPKH,
    limit=5
)

for account in accounts:
    print(f"Address: {account.address}")
    print(f"Private Key: {account.private}")
    print(f"WIF: {account.wif}")
    print(f"Path: {account.path}")
```

### Blockchain API Integration

```python
import asyncio
from mm_btc.blockstream import BlockstreamClient

async def get_address_info():
    client = BlockstreamClient(testnet=False)
    
    # Get address information
    address_info = await client.get_address("bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh")
    if address_info.is_ok():
        print(f"Balance: {address_info.value.chain_stats.funded_txo_sum}")
    
    # Get UTXOs
    utxos = await client.get_utxo("bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh")
    if utxos.is_ok():
        for utxo in utxos.value:
            print(f"TXID: {utxo.txid}, Value: {utxo.value}")

asyncio.run(get_address_info())
```


## CLI Usage

The `mm-btc` command provides several subcommands for Bitcoin operations.

### Mnemonic Operations

```bash
# Generate a new 12-word mnemonic and derive addresses
mm-btc mnemonic

# Use existing mnemonic with custom parameters
mm-btc mnemonic -m "your twelve word mnemonic phrase here..." -l 5 --address-type P2WPKH

# Generate testnet addresses
mm-btc mnemonic --testnet --path bip84

# Use custom derivation path
mm-btc mnemonic --path "m/44'/0'/0'/0" --hex
```

### Address Information

```bash
# Get address information from Blockstream API
mm-btc address bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh

# Get UTXOs for an address
mm-btc utxo bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh
```

### Transaction Operations

```bash
# Create a transaction from config file
mm-btc create-tx config.toml

# Decode a transaction
mm-btc decode-tx 02000000000101... --testnet
```

### Configuration Example

Create a `config.toml` file for transaction creation:

```toml
from_address = "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
private = "your_private_key_wif_format"

[[outputs]]
address = "bc1qrecipient_address_here"
amount = 50000  # Amount in satoshis

[[outputs]]
address = "bc1qanother_recipient"
amount = 25000
```

## Address Types

Supported Bitcoin address types:

- `P2PKH` - Pay to Public Key Hash (Legacy)
- `P2SH` - Pay to Script Hash
- `P2WPKH` - Native SegWit (Bech32)
- `P2WPKH_IN_P2SH` - SegWit wrapped in P2SH
- `P2WSH` - Native SegWit Script
- `P2WSH_IN_P2SH` - SegWit Script wrapped in P2SH  
- `P2TR` - Taproot

## Derivation Paths

- **BIP44**: `m/44'/0'/0'/0` (mainnet) / `m/44'/1'/0'/0` (testnet)
- **BIP84**: `m/84'/0'/0'/0` (mainnet) / `m/84'/1'/0'/0` (testnet)
- **Custom**: Specify your own path like `m/44'/0'/0'/0`


## Dependencies

- `hdwallet` - HD wallet operations
- `bit` - Bitcoin transaction creation
- `bitcoinlib` - Bitcoin utilities
- `mnemonic` - BIP39 mnemonic generation
- `typer` - CLI framework
- `mm-web3` - Cryptocurrency utilities


## References

- [Bitcoin Transactions](https://en.bitcoin.it/wiki/Transaction)
- [Address Prefixes](https://en.bitcoin.it/wiki/List_of_address_prefixes)
- [Bitcoin BIPs](https://github.com/bitcoin/bips/blob/master/README.mediawiki)
- [Blockstream API](https://github.com/Blockstream/esplora/blob/master/API.md)

