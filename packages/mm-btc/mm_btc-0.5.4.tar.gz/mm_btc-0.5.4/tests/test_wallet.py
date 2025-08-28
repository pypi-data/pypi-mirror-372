from mm_btc.wallet import (
    BIP44_MAINNET_PATH,
    BIP44_TESTNET_PATH,
    BIP84_MAINNET_PATH,
    BIP84_TESTNET_PATH,
    AddressType,
    derive_accounts,
    generate_mnemonic,
)


def test_generate_mnemonic():
    mnemonic = generate_mnemonic(words=24)
    assert len(mnemonic.split()) == 24

    assert generate_mnemonic() != generate_mnemonic()


def test_derive_accounts(mnemonic, passphrase):
    # mainnet bip44
    accs = derive_accounts(mnemonic, passphrase, BIP44_MAINNET_PATH, AddressType.P2PKH, 2)
    assert accs[1].path == "m/44'/0'/0'/0/1"
    assert accs[1].address == "13MJrGQq8RwLcGfdnY58666kCsZqevsadE"
    assert accs[1].private == "0d5feb50af849f2ebcc0c83a4446ddbceefd7b0ceba437a57161fa37702d096e"
    assert accs[1].wif == "Kwfi75WxsuaKnmxRUQDoEZDzKXkMC8E9Pzk3vVjEdPsJu1DXCFPv"

    # mainnet bip84
    accs = derive_accounts(mnemonic, passphrase, BIP84_MAINNET_PATH, AddressType.P2WPKH, 2)
    assert accs[1].path == "m/84'/0'/0'/0/1"
    assert accs[1].address == "bc1qszqeg6gfcmt8zurkeayes2895urnea2m54rt3w"
    assert accs[1].private == "1cc57553f9e3e1b863693be92ac753f682f61f1a2dede2ceff97262027635334"
    assert accs[1].wif == "KxBdzQTQduYKoec1FWgwMDF9R1a4UdQp3ezyhjniw4W2k54Cb6gE"

    # testnet bip44
    accs = derive_accounts(mnemonic, passphrase, BIP44_TESTNET_PATH, AddressType.P2PKH, 2)
    assert accs[1].path == "m/44'/1'/0'/0/1"
    assert accs[1].address == "miRfXh2aH6pjhdo5EoBt4RRdAipR88dcV3"
    assert accs[1].private == "3a2e8fc45c75ab8a7cdafacf7c77c941f8eebc813ee2f0e17ee86e7ac8584b3a"
    assert accs[1].wif == "cPXoLA4cRKxeht4iH6ZsCDQxPspFi8SEieZNTKDzGgog94Zg5Y64"

    # testnet bip84
    accs = derive_accounts(mnemonic, passphrase, BIP84_TESTNET_PATH, AddressType.P2WPKH, 2)
    assert accs[1].path == "m/84'/1'/0'/0/1"
    assert accs[1].address == "tb1qp36pk9w408pgfpwn5myxwurr3fhzryn0lpyah2"
    assert accs[1].private == "150fd20e4cb377ae57b43fed59ca2765a9f5d91a20640a4cfdf43ceb5403d48c"
    assert accs[1].wif == "cNHeFPcfq2XFfDAgq9icSK8NX29C1exPHekqYQdWgruQ6gPMBmXD"
