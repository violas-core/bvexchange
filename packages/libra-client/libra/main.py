
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

# from datetime import datetime
# client = Client.new(**violas_config)
# tx = "4aefeb809e2986273d7695c7130ef2eb2ff18fe04f686bab94569884b1ae5ce01d0000000000000002000000b80000004c49425241564d0a010007014a00000004000000034e000000060000000d54000000060000000e5a0000000600000005600000002900000004890000002000000008a90000000f00000000000001000200010300020002040200030204020300063c53454c463e0c4c696272614163636f756e74046d61696e0f7061795f66726f6d5f73656e6465720000000000000000000000000000000000000000000000000000000000000000000100020004000c000c0113010102020000000100000045876ba44dc5de68218138283713bb6eeca643eb25959697679f5d0f3c2c1b860000000080841e0000000000c04504000000000000000000000000005a2e035e00000000200000006032d9699ec90d49906832bdeacbaafe8f39769c14a30b737a33079ab413bb5e40000000a7adf05508f862c11d04e5ae4bd37f708e964bac6e06432678c34fee634e232f3529d4a57af1794a4fc815e589025fe6390b416dfa4e71612deec7e517cb390d"
# print(SignedTransaction.deserialize(bytes.fromhex(tx)))
# print(datetime.now().timestamp())
# client.submit_signed_txn(tx, is_blocking=True)

wallet = WalletLibrary.recover("/root/recover")
a1 = wallet.accounts[0]
print(a1.private_key.hex())
print(a1.public_key.hex())
print(a1.address.hex())

# a1 = wallet.new_account()
# a2 = wallet.new_account()
# client.mint_coins(a1.address, 100, is_blocking=True)
# tx = client.gen_signed_transaction(a1, a2.address, 100)
# print(client.parse_signed_txn(tx))








