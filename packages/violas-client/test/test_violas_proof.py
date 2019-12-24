from libra import Client, WalletLibrary
from libra.client import *
from libra.proof.account_state_with_proof import AccountStateWithProof
from libra.proof import verify_transaction_info

host="125.39.5.57"
port = 46454
validator_set_file="../libra/consensus_peers.config.toml"
faucet_file="../libra/temp_faucet_keys"
mint_address = bytes.fromhex("000000000000000000000000000000000000000000000000000000000a550c18")



def test_transaction_info_proof():
    wallet = WalletLibrary.new()
    client = Client.new(host, port, validator_set_file, faucet_file)
    a1 = wallet.new_account()
    client.mint_coins(a1.address, 100, is_blocking=True)
    version = client.get_latest_transaction_version()
    request = UpdateToLatestLedgerRequest()
    item = request.requested_items.add()
    item.get_account_state_request.address =a1.address
    resp = client.update_to_latest_ledger(request)


def test_account_state_proof():
    wallet = WalletLibrary.new()
    client = Client.new(host, port, validator_set_file, faucet_file)
    a1 = wallet.new_account()
    client.mint_coins(a1.address, 100, is_blocking=True)
    request = UpdateToLatestLedgerRequest()
    item = request.requested_items.add()
    item.get_account_state_request.address =a1.address
    resp = client.update_to_latest_ledger(request)

    account_state_proof = resp.response_items[0].get_account_state_response.account_state_with_proof
    # siblings = account_state_proof.proof.transaction_info_to_account_proof.siblings
    ledger_info = resp.ledger_info_with_sigs.ledger_info
    version = resp.ledger_info_with_sigs.ledger_info.version
    # event_with_proof = resp.response_items[0].get_account_state_response.account_state_with_proof.blob
    AccountStateWithProof.verify(account_state_proof, ledger_info, version, a1.address)


def test_transaction_proof():
    pass

