#!/usr/bin/python3

import sys, os, time
import json
sys.path.append(os.getcwd())
sys.path.append(f"..")

import web3
from web3 import Web3

class vlsmproofdatasslot():

    def __init__(self, contract, name = "vlsmproofdatas"):
        self._contract = contract
        self._name = name
        self._functions = contract.functions

    def slot_name(self):
        return self._name

    def name(self):
        return self._functions.name().call()

    def symbol(self):
        return self._functions.symbol().call()

    def raw_granted_mng_permission(self, address):
        return self._functions.grantedMngPermission(address)

    def raw_pause(self):
        return self._functions.pause()

    def raw_revoke_mng_permission(self, address):
        return self._functions.revokeMngPermission(address)

    def raw_transfer_owner_ship(self, address):
        return self._functions.transferOwnership(address)

    def raw_transfer_proof(self, token_address, datas):
        return self._functions.transferProof(token_address, datas)

    def raw_transfer_proof_state_with_addr(self, address, sequence, state):
        return self._functions.transferProofState(address, sequence, state)

    def raw_transfer_proof_state_with_version(self, version, state):
        return self._functions.transferProofState(version, state)

    def manage_role_state(self, address):
        return self._functions.manageRoleState(address).call()

    def owner(self):
        return self._functions.owner().call()

    def proof_info_with_addr(self, address, sequence):
        return self._functions.proofInfo(address, sequence).call()

    def proof_info_with_version(self, version):
        return self._functions.proofInfo(version).call()

    def proof_address_sequence(self, address):
        return self._functions.accountSequence(address).call()

    def proof_address_version(self, address, sequence):
        return self._functions.accountVersion(address, sequence).call()

    def proof_address_latest_version(self, address):
        return self._functions.accountLatestVersion(address).call()

    def state_address(self):
        return self._functions.stateAddress().call()

    def next_version(self):
        return self._functions.nextVersion().call()

    def __getattr__(self, name):
        print(f"calling {name}")

def test():

    from datas.abis.usdt_abi import (
            USDT_ABI,
            USDT_BYTECODE
            )
    from datas.abis.vlsmproof_abi import (
            VLSMPROOF_ABI,
            VLSMPROOF_BYTECODE
            )
    contract_codes = {
            "usdt" : {"abi":USDT_ABI, "bytecode":USDT_BYTECODE, "token_type": "erc20"},
            "vlsmproof": {"abi":VLSMPROOF_ABI, "bytecode": VLSMPROOF_BYTECODE, "token_type": "vlsmproof"}
            }

    #host = "http://127.0.0.1:8545"
    host = "http://51.140.241.96:8545"
    w3 = Web3(Web3.HTTPProvider(host))
    if not w3.isConnected():
        raise Exception("not connect {host}")
    else:
        print("connected parity")

    usdt_address = "0x6f08730da8e7de49a4064d2217c6b68d7e61e727"
    contract_address = "0xE6C7f2DAB2E9B16ab124E45dE3516196457A1120"
    vmp = vlsmproofslot(w3.eth.contract(Web3.toChecksumAddress(contract_address), abi=contract_codes["vlsmproof"]["abi"]), "vlsmproof")

    account = "0x89fF4a850e39A132614dbE517F80603b4A96fa0A"
    account1_privkey = '05849aa606c43ef46e1d71381573221538caef578973fb26f9b889b382d568bd'
    account2 = "0x9382690D0B835b69FD9C0bc23EB772a0Ddb3613F"

    #update_proof_state(w3, vmp, account, account1_privkey)

def get_transactions(vmp):
    datas = vmp.get_transactions(0, vmp.next_version())
    for data in datas:
        print(data.to_json())

def update_proof_state_with_ver(w3, vmp, account, account1_privkey, version):
    print(f'''
    block number: {w3.eth.blockNumber}
    syncing: {w3.eth.syncing}
    ''')


    print(f"proof info: data   sequence  state  token   sender amount")
    nonce = w3.eth.getTransactionCount(Web3.toChecksumAddress(account))
    proof_info = vmp.proof_info_with_version(version)
    print(f"proof info[{i}]: {proof_info}")
    state = proof_info[2]
    if  state != 1: 
        print(f"version({i}) state({state}) is not 1, next version")
        return

    print(f"start version: {i}")
    gasLimit = w3.eth.getBlock(w3.eth.blockNumber).get("gasLimit")
    txn = vmp.raw_transfer_proof_state_with_version(i, 3).buildTransaction({
        'chainId': 42, #kovan
        'gas':gasLimit,
        #'gasPrice': Web3.toWei(1, 'gwei'),
        'gasPrice': w3.eth.gasPrice + Web3.toWei(100, 'gwei'),
        'nonce': nonce,
        })
    print(f"txn:{txn}")
    signed_txn = w3.eth.account.sign_transaction(txn, private_key=account1_privkey)
    print(f"tx hash:{w3.toHex(signed_txn.hash)}")
    print(f"tx rawtransaction:{w3.toHex(signed_txn.rawTransaction)}")
    txhash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    print(f"ret tx hash:{w3.toHex(txhash)}")

    #w3.eth.waitForTransactionReceipt(txhash)
    
def update_proof_state(w3, vmp, account, account1_privkey):
    print(f'''
    block number: {w3.eth.blockNumber}
    syncing: {w3.eth.syncing}
    ''')

    print(f'''
contract info:
    contract name: {vmp.slot_name()}
    name: {vmp.name()}
    symbol:{vmp.symbol()}
    conract_version: {vmp.contract_version()}
    current_balance: {vmp.current_balance()}
    next_version: {vmp.next_version()}
    owner : {vmp.owner()}
    payee : {vmp.payee()} 
    block number: {w3.eth.blockNumber}
    syncing: {w3.eth.syncing}
    gasLimit: {w3.eth.getBlock("latest").get("gasLimit")}
    ''')


    print(f"proof info: data   sequence  state  token   sender amount")
    nonce = w3.eth.getTransactionCount(Web3.toChecksumAddress(account))
    for i in range(vmp.next_version()):
        proof_info = vmp.proof_info_with_version(i)
        print(f"proof info[{i}]: {proof_info}")
        state = proof_info[2]
        if  state != 1: 
            print(f"version({i}) state({state}) is not 1, next version")
            continue

        print(f"start version: {i}")
        gasLimit = w3.eth.getBlock("latest").get("gasLimit")
        txn = vmp.raw_transfer_proof_state_with_version(i, 3).buildTransaction({
            'chainId': 42, #kovan
            'gas':gasLimit,
            #'gasPrice': Web3.toWei(1, 'gwei'),
            'gasPrice': w3.eth.gasPrice + Web3.toWei(100, 'gwei'),
            'nonce': nonce,
            })
        print(f"txn:{txn}")
        signed_txn = w3.eth.account.sign_transaction(txn, private_key=account1_privkey)
        print(f"tx hash:{w3.toHex(signed_txn.hash)}")
        print(f"tx rawtransaction:{w3.toHex(signed_txn.rawTransaction)}")
        txhash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        print(f"ret tx hash:{w3.toHex(txhash)}")

        #w3.eth.waitForTransactionReceipt(txhash)
    
if __name__ == "__main__":
    test()
