
from libra import WalletLibrary
from libra import Client
from libra.json_print import json_print


# network="18.220.66.235"
# port = 40001
# validator_set_file="/root/violas_config/consensus_peers.config.toml"
# faucet_file="/root/violas_config/temp_faucet_keys"

network="ac.testnet.libra.org"
port = 8000
validator_set_file="/root/libra_config/consensus_peers.config.toml"
faucet_file=None

client = Client.new(network, port, validator_set_file, faucet_file)
json_print(client.get_transaction(3138, True).to_json())

