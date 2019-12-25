from libra import Client
from libra import WalletLibrary
from libra import AccountError, TransactionIllegalError, TransactionNotExistError

# # tmp_config = {
# "host": "localhost",
# "port": 34943,
# "validator_set_file": "/tmp/9f062c60e0d4384c34f8b749ff6c89c1/0/consensus_peers.config.toml",
# "faucet_file": "/tmp/5aec89e92848a55db1f475823a8cd330/temp_faucet_keys"
# }
network = "localhost"
port = 45939
validator_set_file =  "/tmp/df065e7b8944676acf685a61324f2548/0/consensus_peers.config.toml"
faucet_file = "/tmp/7dd1d1b3bd54ee11731c93c8c8683e88/temp_faucet_keys"

platform_address = bytes.fromhex("0000000000000000000000000000000000000000000000000000000000000000")
platform_mint_address = bytes.fromhex("000000000000000000000000000000000000000000000000000000000a550c18")

def test_account_args():
    wallet = WalletLibrary.new()
    client = Client.new(network, port, validator_set_file, faucet_file)
    a1 = wallet.new_account()
    a2 = wallet.new_account()
    client.mint_coins(a1.address, 100, is_blocking=True)
    client.transfer_coin(a1, a2.address, 10, is_blocking=True)
    client.get_account_blob(a1.address)
    client.get_account_blob(a1.address.hex())
    client.get_account_state(a1.address)
    client.get_account_state(a1.address.hex())
    client.get_account_event(a1.address, 0)
    client.get_account_event(a1.address.hex(), 0)
    client.get_account_resource(a1.address)
    client.get_account_resource(a1.address.hex())

def test_transaction_args():
    wallet = WalletLibrary.new()
    client = Client.new(network, port, validator_set_file, faucet_file)
    a1 = wallet.new_account()
    a2 = wallet.new_account()
    client.mint_coins(a1.address, 100, is_blocking=True)
    client.mint_coins(a2.address.hex(), 100, is_blocking=True)
    client.transfer_coin(a1, a2.address, 10, is_blocking=True)
    client.transfer_coin(a1, a2.address.hex(), 10, is_blocking=True)

    client.violas_publish(a1, is_blocking=True)
    client.violas_init(a1, a1.address, is_blocking=True)
    client.violas_init(a2, a1.address.hex(), is_blocking=True)

    client.violas_mint_coin(a2.address, 100, a1, is_blocking=True)
    client.violas_mint_coin(a1.address.hex(), 100, a1, is_blocking=True)
    client.violas_transfer_coin(a1, a2.address.hex(), 10, a1.address.hex(), is_blocking=True)
    client.violas_transfer_coin(a1, a2.address, 10, a1.address, is_blocking=True)

    client.violas_make_order(a1, a1.address, 10 ,10, is_blocking=True)
    client.violas_pick_order(a1, a1.address, a1.address, 10, 10, is_blocking=True)
    client.violas_make_order(a1, a1.address.hex(), 10 ,10, is_blocking=True)
    client.violas_pick_order(a1, a1.address.hex(), a1.address.hex(), 10, 10, is_blocking=True)

    client.violas_make_order(a1, a1.address.hex(), 10, 10, is_blocking=True)
    client.violas_withdraw_order(a1, a1.address.hex(), is_blocking=True)
    client.violas_make_order(a1, a1.address.hex(), 10, 10, is_blocking=True)
    client.violas_withdraw_order(a1, a1.address, is_blocking=True)


def test_violas_account_error():
    client = Client.new(network, port, validator_set_file, faucet_file)
    try:
        client.get_account_blob("0b6aff81e97a9b66b3356d0bd1bb8ac9326e79eb459bc25649282fcab7a40065")
    except AccountError:
        pass

    try:
        client.get_account_state("0b6aff81e97a9b66b3356d0bd1bb8ac9326e79eb459bc25649282fcab7a40065")
    except AccountError:
        pass

    try:
        client.get_account_resource("0b6aff81e97a9b66b3356d0bd1bb8ac9326e79eb459bc25649282fcab7a40065")
    except AccountError:
        pass

    try:
        client.get_account_event("0b6aff81e97a9b66b3356d0bd1bb8ac9326e79eb459bc25649282fcab7a40065", 0)
    except AccountError:
        pass

    try:
        client.violas_get_balance("0b6aff81e97a9b66b3356d0bd1bb8ac9326e79eb459bc25649282fcab7a40065", "1111")
    except AccountError:
        pass

    try:
        client.violas_get_info("0b6aff81e97a9b66b3356d0bd1bb8ac9326e79eb459bc25649282fcab7a40065")
    except AccountError:
        pass


def test_violas_transaction_error():
    version = 1000000
    wallet = WalletLibrary.new()
    client = Client.new(network, port, validator_set_file, faucet_file)
    a1 = wallet.new_account()
    a2 = wallet.new_account()
    try:
        client.get_transaction(version)
    except TransactionNotExistError:
        pass

    try:
        client.get_account_transaction(a1.address, version)
    except TransactionNotExistError:
        pass

    try:
        client.get_tx_events(version)
    except TransactionNotExistError:
        pass

    try:
        client.get_account_transaction_proto(a1.address, version, True)
    except TransactionNotExistError:
        pass

def test_violas_exchange():
    wallet = WalletLibrary.new()
    client = Client.new(network, port, validator_set_file, faucet_file)
    a1 = wallet.new_account()
    a2 = wallet.new_account()
    client.mint_coins(a1.address, 100, is_blocking=True)
    client.mint_coins(a2.address, 100, is_blocking=True)
    client.violas_publish(a1, True)
    client.violas_publish(a2, True)
    client.violas_init(a1, a1.address, True)
    client.violas_init(a2, a1.address, True)
    client.violas_init(a1, a2.address, True)
    client.violas_init(a2, a2.address, True)
    client.violas_mint_coin(a1.address, 100, a1, True)
    client.violas_mint_coin(a1.address, 100, a2, True)
    client.violas_make_order(a1, a1.address, 10, 10, is_blocking=True)
    client.violas_make_order(a1, a2.address, 10, 10, is_blocking=True)
    assert 90 == client.violas_get_balance(a1.address, a1.address)
    assert 90 == client.violas_get_balance(a1.address, a2.address)
    client.violas_pick_order(a2, a1.address, a1.address, 10, 10, is_blocking=True)
    assert 110 == client.get_balance(a1.address)
    assert 90 == client.get_balance(a2.address)
    assert 90 == client.violas_get_balance(a1.address, a1.address)
    assert 10 == client.violas_get_balance(a2.address, a1.address)
    client.violas_withdraw_order(a1, a2.address, is_blocking=True)
    assert 100 == client.violas_get_balance(a1.address, a2.address)
    client.violas_make_order(a1, a1.address, 10, 10, is_blocking=True)
    client.violas_make_order(a1, a2.address, 10, 10, is_blocking=True)
    assert 80 == client.violas_get_balance(a1.address, a1.address)
    assert 90 == client.violas_get_balance(a1.address, a2.address)
    client.violas_pick_order(a2, a1.address, a1.address, 10, 10, is_blocking=True)
    assert 80 == client.violas_get_balance(a1.address, a1.address)
    assert 90 == client.violas_get_balance(a1.address, a2.address)


def test_violas_exchange2():
    wallet = WalletLibrary.new()
    client = Client.new(network, port, validator_set_file, faucet_file)
    a1 = wallet.new_account()
    a2 = wallet.new_account()
    client.mint_coins(a1.address, 100, is_blocking=True)
    client.mint_coins(a2.address, 100, is_blocking=True)
    client.violas_publish(a1, True)
    client.violas_publish(a2, True)
    client.violas_owner_init(a1, "this is a1", True)
    client.violas_init(a2, a1.address, True)
    client.violas_init(a1, a2.address, True)
    client.violas_owner_init(a2, "this is a2", True)
    client.violas_mint_coin(a1.address, 100, a1, True)
    client.violas_mint_coin(a2.address, 100, a1, True)
    client.violas_make_order(a1, a1.address, 10, 10, vcoin_to_scoin=1, is_blocking=True)
    assert 90 == client.get_balance(a1.address)
    client.violas_pick_order(a2, a1.address, a1.address, 10, 10, vcoin_to_scoin=1, is_blocking=True)
    assert 90 == client.violas_get_balance(a2.address, a1.address)
    assert 110 == client.get_balance(a2.address)
    assert 110 == client.violas_get_balance(a1.address, a1.address)
    assert 90 == client.get_balance(a1.address)


def test_violas_event():
    wallet = WalletLibrary.new()
    client = Client.new(network, port, validator_set_file, faucet_file)
    a1 = wallet.new_account()
    a2 = wallet.new_account()

    client.mint_coins(a1.address, 100, True)
    client.mint_coins(a2.address, 100, True)
    client.violas_publish(a1, True)
    seq = client.get_sequence_number(a1.address)
    version = client.get_transaction_version(a1.address, seq-1)
    tx_events = client.get_tx_events(version)
    assert 0 == len(tx_events)
    client.violas_init(a1, a1.address, True)
    client.violas_init(a2, a1.address, True)
    seq = client.get_sequence_number(a1.address)
    version = client.get_transaction_version(a1.address, seq-1)
    tx_events = client.get_tx_events(version)
    assert 1 == len(tx_events)
    assert 0 == tx_events[0].get_sequence_number()
    assert a1.address.hex() == tx_events[0].get_module_address()
    assert "ViolasToken" == tx_events[0].get_moudle()
    assert "AllInOneEvent" == tx_events[0].get_name()

    client.violas_mint_coin(a1.address, 100, a1, True)
    seq = client.get_sequence_number(a1.address)
    version = client.get_transaction_version(a1.address, seq-1)
    tx_events = client.get_tx_events(version)
    assert 2 == len(tx_events)
    assert 1 == tx_events[0].get_sequence_number()
    assert 2 == tx_events[1].get_sequence_number()
    assert a1.address.hex() == tx_events[0].get_module_address()
    assert "ViolasToken" == tx_events[0].get_moudle()
    assert "AllInOneEvent" == tx_events[0].get_name()

    client.violas_transfer_coin(a1, a2.address, 10, a1.address, is_blocking=True)
    seq = client.get_sequence_number(a1.address)
    version = client.get_transaction_version(a1.address, seq-1)
    tx_events = client.get_tx_events(version)
    assert 2 == len(tx_events)
    assert 3 == tx_events[0].get_sequence_number()
    assert a1.address.hex() == tx_events[0].get_module_address()
    assert "ViolasToken" == tx_events[0].get_moudle()
    assert "AllInOneEvent" == tx_events[0].get_name()

    client.violas_make_order(a1, a1.address, 10, 10, is_blocking=True)
    seq = client.get_sequence_number(a1.address)
    version = client.get_transaction_version(a1.address, seq-1)
    tx_events = client.get_tx_events(version)
    assert 1 == len(tx_events)
    assert 4 == tx_events[0].get_sequence_number()
    assert a1.address.hex() == tx_events[0].get_module_address()
    assert "ViolasToken" == tx_events[0].get_moudle()
    assert "AllInOneEvent" == tx_events[0].get_name()

    client.violas_withdraw_order(a1, a1.address, is_blocking=True)
    seq = client.get_sequence_number(a1.address)
    version = client.get_transaction_version(a1.address, seq-1)
    tx_events = client.get_tx_events(version)
    assert 1 == len(tx_events)
    assert 5 == tx_events[0].get_sequence_number()
    assert a1.address.hex() == tx_events[0].get_module_address()
    assert "ViolasToken" == tx_events[0].get_moudle()
    assert "AllInOneEvent" == tx_events[0].get_name()

    client.violas_make_order(a1, a1.address, 10, 10, is_blocking=True)
    client.violas_pick_order(a2, a1.address, a1.address, 10, 10, is_blocking=True)
    seq = client.get_sequence_number(a2.address)
    version = client.get_transaction_version(a2.address, seq-1)
    tx_events = client.get_tx_events(version)
    assert 4 == len(tx_events)
    assert 7 == tx_events[3].get_sequence_number()
    assert a1.address.hex() == tx_events[2].get_module_address()
    assert "ViolasToken" == tx_events[2].get_moudle()
    assert "AllInOneEvent" == tx_events[2].get_name()
    assert tx_events[0].is_libra_event()
    assert tx_events[2].is_violas_event()


def test_violas_tx():
    wallet = WalletLibrary.new()
    client = Client.new(network, port, validator_set_file, faucet_file)
    a1 = wallet.new_account()
    a2 = wallet.new_account()

    client.mint_coins(a1.address, 100, True)
    client.mint_coins(a2.address, 100, True)
    seq = client.get_sequence_number(platform_mint_address)
    version = client.get_transaction_version(platform_mint_address, seq-1)
    tx = client.get_transaction(version, True)
    assert platform_mint_address.hex() == tx.get_sender_address()
    assert a2.address.hex() == tx.get_receiver_address()
    assert platform_address.hex() == tx.get_sender_module_address()
    assert platform_address.hex() == tx.get_receiver_module_address()

    client.transfer_coin(a1, a2.address, 10, is_blocking=True)
    seq = client.get_sequence_number(a1.address)
    version = client.get_transaction_version(a1.address, seq-1)
    tx = client.get_transaction(version, True)
    assert a1.address.hex() == tx.get_sender_address()
    assert a2.address.hex() == tx.get_receiver_address()
    assert platform_address.hex() == tx.get_sender_module_address()
    assert platform_address.hex() == tx.get_receiver_module_address()

    client.violas_publish(a1, True)
    seq = client.get_sequence_number(a1.address)
    version = client.get_transaction_version(a1.address, seq-1)
    tx = client.get_transaction(version, True)
    assert a1.address.hex() == tx.get_sender_address()

    client.violas_init(a1, a1.address, True)
    client.violas_init(a2, a1.address, True)
    seq = client.get_sequence_number(a2.address)
    version = client.get_transaction_version(a2.address, seq-1)
    tx = client.get_transaction(version, True)
    assert a2.address.hex() == tx.get_sender_address()
    assert a1.address.hex() == tx.get_sender_module_address()

    client.violas_mint_coin(a2.address, 100, a1, True)
    seq = client.get_sequence_number(a1.address)
    version = client.get_transaction_version(a1.address, seq-1)
    tx = client.get_transaction(version, True)
    assert a1.address.hex() == tx.get_sender_address()
    assert a2.address.hex() == tx.get_receiver_address()
    assert a1.address.hex() == tx.get_sender_module_address()
    assert a1.address.hex() == tx.get_receiver_module_address()

    client.violas_transfer_coin(a2, a1.address, 10, a1.address, is_blocking=True)
    seq = client.get_sequence_number(a2.address)
    version = client.get_transaction_version(a2.address, seq-1)
    tx = client.get_transaction(version, True)
    assert a2.address.hex() == tx.get_sender_address()
    assert a1.address.hex() == tx.get_receiver_address()
    assert a1.address.hex() == tx.get_sender_module_address()
    assert a1.address.hex() == tx.get_receiver_module_address()

    client.violas_make_order(a2, a1.address, 10, 10, is_blocking=True)
    seq = client.get_sequence_number(a2.address)
    version = client.get_transaction_version(a2.address, seq-1)
    tx = client.get_transaction(version, True)
    assert a2.address.hex() == tx.get_sender_address()
    assert a1.address.hex() == tx.get_sender_module_address()
    assert platform_address.hex() == tx.get_receiver_module_address()

    client.violas_pick_order(a1, a1.address, a2.address, 10, 10, is_blocking=True)
    seq = client.get_sequence_number(a1.address)
    tx = client.get_account_transaction(a1.address, seq-1, True)
    assert a1.address.hex() == tx.get_sender_address()
    assert a2.address.hex() == tx.get_receiver_address()
    assert platform_address.hex() == tx.get_sender_module_address()
    assert a1.address.hex() == tx.get_receiver_module_address()

    client.violas_make_order(a2, a1.address, 10, 10, is_blocking=True)
    client.violas_withdraw_order(a2, a1.address, is_blocking=True)
    seq = client.get_sequence_number(a2.address)
    tx = client.get_account_transaction(a2.address, seq-1, True)
    assert a2.address.hex() == tx.get_sender_address()
    assert a1.address.hex() == tx.get_sender_module_address()
    assert a1.address.hex() == tx.get_receiver_module_address()


def test_with_data():
    wallet = WalletLibrary.new()
    client = Client.new(network, port, validator_set_file, faucet_file)
    a1 = wallet.new_account()
    a2 = wallet.new_account()
    client.mint_coins(a1.address, 100, True)
    client.mint_coins(a2.address, 100, True)
    data = "{}"
    client.transfer_coin(a1, a2.address, 10, is_blocking=True)

    client.violas_publish(a1, True)
    client.violas_owner_init(a1, data, is_blocking=True)
    client.violas_init(a2, a1.address, is_blocking=True)

    client.violas_mint_coin(a1.address, 100, a1, is_blocking=True)
    client.violas_transfer_coin(a1, a2.address, 10, a1.address,data=data, is_blocking=True)
    assert client.violas_get_balance(a1.address, a1.address) == 90
    client.violas_withdraw_exchange(a1, a2.address, a1.address, 10, is_blocking=True)


def test_violas_get_order():
    wallet = WalletLibrary.new()
    client = Client.new(network, port, validator_set_file, faucet_file)
    a1 = wallet.new_account()
    a2 = wallet.new_account()
    client.mint_coins(a1.address, 100, is_blocking=True)
    client.mint_coins(a2.address, 100, is_blocking=True)
    client.violas_publish(a1, True)
    client.violas_init(a1, a1.address, True)
    client.violas_init(a2, a1.address, True)
    client.violas_mint_coin(a1.address, 100, a1, True)
    client.violas_make_order(a1, a1.address, 10, 10, is_blocking=True)
    assert 90 == client.violas_get_balance(a1.address, a1.address)
    order = client.get_account_state(a1.address).violas_get_order(a1.address, False)
    assert 10 == order.token
    assert 10 == order.price


def test_submit_signed_txn():
    wallet = WalletLibrary.new()
    client = Client.new(network, port, validator_set_file, faucet_file)
    a1 = wallet.new_account()
    a2 = wallet.new_account()
    client.mint_coins(a1.address, 100, is_blocking=True)
    tx = client.gen_signed_transaction(a1, a2.address, 10)
    client.submit_signed_txn(tx, is_blocking=True)

