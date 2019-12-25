
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
    "host": "125.39.5.57",
    "port": 40001,
    "validator_set_file": None,
    "faucet_file": None
}

violas_hosts = ["51.140.241.96", "13.68.141.242", "18.220.66.235", "52.27.228.84", "47.52.195.50"]
violas_config = {
    'host': "18.220.66.235",
    "port": 40001,
    "validator_set_file": "/root/violas_config/consensus_peers.config.toml",
    "faucet_file": "/root/violas_config/temp_faucet_keys"
}

tmp_config = {
    "host": "localhost",
    "port": 45939,
    "validator_set_file": "/tmp/df065e7b8944676acf685a61324f2548/0/consensus_peers.config.toml",
    "faucet_file": "/tmp/7dd1d1b3bd54ee11731c93c8c8683e88/temp_faucet_keys"
}

client = Client.new(**tmp_config)
wallet = WalletLibrary.new()
a1 = wallet.new_account()
a2 = wallet.new_account()
client.mint_coins(a1.address, 100, is_blocking=True)
tx = client.gen_signed_transaction(a1, a2.address, 100)
print(client.parse_signed_txn(tx))








