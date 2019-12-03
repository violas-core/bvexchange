
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

# network="18.220.66.235"
# port = 40001
# validator_set_file="/root/violas_config/consensus_peers.config.toml"
# faucet_file="/root/violas_config/temp_faucet_keys"

# network="ac.testnet.libra.org"
# port = 8000
# validator_set_file="/root/libra_config/consensus_peers.config.toml"
# faucet_file=None

network="125.39.5.57"
port = 46454
validator_set_file="../libra/consensus_peers.config.toml"
faucet_file="../libra/temp_faucet_keys"

# network="localhost"
# port = 43051
# validator_set_file="/tmp/8d4f2887cefbd791f37e4e739f4676d4/0/consensus_peers.config.toml"
# faucet_file="/tmp/474794edcdc9b04b7640686f79382d77/temp_faucet_keys"


wallet = WalletLibrary.new()
client = Client.new(network, port, validator_set_file, faucet_file)
a1 = wallet.new_account()
a2 = wallet.new_account()
client.mint_coins(a1.address, 100, is_blocking=True)
client.transfer_coin(a1, a2.address, 10, is_blocking=True)
print(client.get_latest_transaction_version())
client.violas_publish(a1, is_blocking=True)

version = client.get_latest_transaction_version()
json_print(client.get_transaction(version).to_json())
# a1 = wallet.new_account()
# address = bytes.fromhex("000000000000000000000000000000000000000000000000000000000a550c18")
# address = bytes.fromhex("0000000000000000000000000000000000000000000000000000000000000000")
#
# request = UpdateToLatestLedgerRequest()
# item = request.requested_items.add()
# item.get_account_state_request.address =address
# resp = client.update_to_latest_ledger(request)
#
# account_state_proof = resp.response_items[0].get_account_state_response.account_state_with_proof
# siblings = account_state_proof.proof.transaction_info_to_account_proof.siblings
# ledger_info = resp.ledger_info_with_sigs.ledger_info
# version = resp.ledger_info_with_sigs.ledger_info.version
# # address = bytes.fromhex(a1)
# event_with_proof = resp.response_items[0].get_account_state_response.account_state_with_proof.blob
# AccountStateWithProof.verify(account_state_proof, ledger_info, version, address)

