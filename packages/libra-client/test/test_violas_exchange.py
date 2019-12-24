from libra import Client
from libra import WalletLibrary

from libra.violas_transaction import LegalTender

network="localhost"
port = 34943
validator_set_file="/tmp/9f062c60e0d4384c34f8b749ff6c89c1/0/consensus_peers.config.toml"
faucet_file="/tmp/5aec89e92848a55db1f475823a8cd330/temp_faucet_keys"


platform_address = bytes.fromhex("0000000000000000000000000000000000000000000000000000000000000000")
platform_mint_address = bytes.fromhex("000000000000000000000000000000000000000000000000000000000a550c18")

def test_violas_submit_exchange():
    wallet = WalletLibrary.new()
    client = Client.new(network, port, validator_set_file, faucet_file)
    a1 = wallet.new_account()
    a2 = wallet.new_account()
    client.mint_coins(a1.address, 100, is_blocking=True)
    client.mint_coins(a2.address, 100, is_blocking=True)
    client.violas_publish(a1, is_blocking=True)
    client.violas_owner_init(a1, LegalTender.USD, is_blocking=True)
    client.violas_init(a2, a1.address, is_blocking=True)
    client.violas_mint_coin(a1.address, 100, a1, is_blocking=True)
    client.violas_submit_exchange(a1, a2.address, 10, a1.address, 10, a1.address, 10, 50, is_blocking=True)
    seq = client.get_sequence_number(a1.address)
    version = client.get_transaction_version(a1.address, seq-1)
    tx = client.get_transaction(version)
    data = tx.get_data()
    assert data["type"] == "sub_ex"
    assert data["addr"] == a1.address.hex()
    assert data["amount"] == 10
    assert 10 == data["fee"]
    assert 50 == data["exp"]

    state = client.get_account_state(a1.address)
    assert 100 == state.get_balance()
    assert 90 == state.violas_get_balance(a1.address.hex())
    assert state.violas_get_tender_name() == LegalTender.USD

def test_violas_feedback_exchange():
    wallet = WalletLibrary.new()
    client = Client.new(network, port, validator_set_file, faucet_file)
    a1 = wallet.new_account()
    a2 = wallet.new_account()
    client.mint_coins(a1.address, 100, is_blocking=True)
    client.mint_coins(a2.address, 100, is_blocking=True)
    client.violas_publish(a1, is_blocking=True)
    client.violas_owner_init(a1, LegalTender.USD, is_blocking=True)
    client.violas_init(a2, a1.address, is_blocking=True)
    client.violas_mint_coin(a1.address, 100, a1, is_blocking=True)
    client.violas_feedback_exchange(a1, a2.address, 10, a1.address, 100, 50, 1, is_blocking=True)
    seq = client.get_sequence_number(a1.address)
    version = client.get_transaction_version(a1.address, seq-1)
    tx = client.get_transaction(version)
    data = tx.get_data()
    assert data["type"] == "fb_ex"
    assert data["ver"] == 100
    assert data["state"] == 1
    assert 50 == data["fee"]

def test_violas_withdraw_exchange():
    wallet = WalletLibrary.new()
    client = Client.new(network, port, validator_set_file, faucet_file)
    a1 = wallet.new_account()
    a2 = wallet.new_account()
    client.mint_coins(a1.address, 100, is_blocking=True)
    client.mint_coins(a2.address, 100, is_blocking=True)
    client.violas_publish(a1, is_blocking=True)
    client.violas_owner_init(a1, LegalTender.USD, is_blocking=True)
    client.violas_init(a2, a1.address, is_blocking=True)
    client.violas_mint_coin(a1.address, 100, a1, is_blocking=True)
    client.violas_withdraw_exchange(a1, a2.address, a1.address, 100, is_blocking=True)
    seq = client.get_sequence_number(a1.address)
    version = client.get_transaction_version(a1.address, seq-1)
    tx = client.get_transaction(version)
    data = tx.get_data()
    assert data["ver"] == 100
    assert data["type"] == "wd_ex"
