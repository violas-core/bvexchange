
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
import collections
violas_hosts = ["51.140.241.96", "13.68.141.242", "18.220.66.235", "52.27.228.84", "47.52.195.50"]
violas_config = {
    'host': "51.140.241.96",
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

client = Client.new(**old_violas_config)
json_print(client.get_transaction(100, True).to_json())
# wallet = WalletLibrary.new()
# a1 = wallet.new_account()
# a2 = wallet.new_account()
# num = 0
# while True:
#     host = violas_hosts[num % 5]
#     s_time = time.time()
#     client = Client.new(host, **violas_config)
#     try:
#         client.mint_coins(a1.address, 100, is_blocking=True)
#     except Exception as e:
#         traceback.print_exc()
#     print(f"Mint Coin;     {time.time()-s_time};   IP:{host};   {num}")
#     s_time = time.time()
#     try:
#         client.transfer_coin(a1, a2.address, 10, is_blocking=True)
#     except Exception as e:
#         traceback.print_exc()
#     print(f"Transfer Coin; {time.time()-s_time};   IP:{host};   {num}")
#     num += 1









