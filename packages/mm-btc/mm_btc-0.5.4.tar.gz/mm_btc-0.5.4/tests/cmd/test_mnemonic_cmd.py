import pytest

from mm_btc.cli.cli import app
from mm_btc.cli.cmd.mnemonic_cmd import get_derivation_path_prefix


def test_get_derivation_path_prefix():
    assert get_derivation_path_prefix("m/11'/0'/0'/0", testnet=True) == "m/11'/0'/0'/0"
    assert get_derivation_path_prefix("bip44", False) == "m/44'/0'/0'/0"
    assert get_derivation_path_prefix("bip44", True) == "m/44'/1'/0'/0"
    assert get_derivation_path_prefix("bip84", False) == "m/84'/0'/0'/0"
    assert get_derivation_path_prefix("bip84", True) == "m/84'/1'/0'/0"

    with pytest.raises(ValueError):
        get_derivation_path_prefix("bip", True)


def test_mnemonic_cmd(cli_runner, mnemonic, passphrase):
    cmd = f"mnemonic -m '{mnemonic}' --passphrase '{passphrase}' -a P2WPKH"
    res = cli_runner.invoke(app, cmd)
    assert res.exit_code == 0
    acc_line = "m/44'/0'/0'/0/7 bc1qvcq77599py2x46weksqf9zvf7a53aw9wefrrhs L3QF5FHUtX2a1ucGgVfrdhdvLHBSxsRQoGsv7tyY8P5Jt7UV9LZv"
    assert acc_line in res.stdout
