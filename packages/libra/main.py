
from libra import WalletLibrary
from libra import Client
from libra.json_print import json_print
from libra.hasher import uint8_to_bits
from canoser import hex_to_int_list
from libra.bytecode import bytecodes
from canoser.util import bytes_to_int_list
from libra.account_address import Address
from libra.hasher import bytes_to_bits
from libra.client import *
from libra.proof.account_state_with_proof import AccountStateWithProof
from threading import Thread
from canoser.util import bytes_to_int_list
from libra.violas_transaction import LegalTender

import traceback

old_violas_config = {
    "host": "ac.testnet.libra.org",
    "port": 8000,
    "validator_set_file": None,
    "faucet_file": None
}

violas_config = {
    "host": "52.151.9.191",
    "port": 40001,
    "validator_set_file": "/root/violas_config/consensus_peers.config.toml",
    "faucet_file": "/root/violas_config/temp_faucet_keys"
}

tmp_config = {
    "host": "localhost",
    "port": 34943,
    "validator_set_file": "/tmp/9f062c60e0d4384c34f8b749ff6c89c1/0/consensus_peers.config.toml",
    "faucet_file": "/tmp/5aec89e92848a55db1f475823a8cd330/temp_faucet_keys"
}

# wallet = WalletLibrary.new()
client = Client("violas_testnet")

# start = 0
# while True:
#     b_time = time.time()
#     while True:
#         try:
#             client.get_transactions(start, 100, True)
#             start += 100
#             print(start, time.time()-b_time)
#             break
#         except Exception as e:
#             traceback.print_exc()
#             continue
# a1 = wallet.new_account()
# a2 = wallet.new_account()
# client.mint_coins(a1.address, 100, is_blocking=True)
# client.mint_coins(a2.address, 100, is_blocking=True)
# client.violas_publish(a1, is_blocking=True)
# client.violas_owner_init(a1, LegalTender.USD, is_blocking=True)
# client.violas_init(a2, a1.address, is_blocking=True)
# client.violas_mint_coin(a1.address, 100, a1, is_blocking=True)
# client.violas_submit_exchange(a1, a2.address, 10, a1.address, 10, a1.address, 10, 50, is_blocking=True)
# seq = client.get_sequence_number(a1.address)
# version = client.get_transaction_version(a1.address, seq - 1)
# tx = client.get_transaction(version)
# data = tx.get_data()
# assert data["type"] == "sub_ex"
# assert data["addr"] == a1.address.hex()
# assert data["amount"] == 10
# assert 10 == data["fee"]
# assert 50 == data["exp"]
#
# state = client.get_account_state(a1.address)
# assert 100 == state.get_balance()
# assert 90 == state.violas_get_balance(a1.address.hex())
# assert state.violas_get_tender_name() == LegalTender.USD






