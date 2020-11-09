#!/usr/bin/python3

import sys, os, time
import json
sys.path.append(os.getcwd())
sys.path.append(f"..")

import web3
from web3 import Web3

class vlsmproofmainslot():

    def __init__(self, contract, name = "vlsmproofmain"):
        self._contract = contract
        self._name = name
        self._functions = contract.functions

    def slot_name(self):
        return self._name

    def name(self):
        return self._functions.name().call()

    def symbol(self):
        return self._functions.symbol().call()

    def raw_transfer(self, token_address, to, value):
        return self._functions.transfer(token_address, to, value)

    def raw_pause(self):
        return self._functions.pause()

    def raw_remove_token_with_name(self, name):
        return self._functions.removeToken(name)

    def raw_revoe_token_with_token(self, address):
        return self._functions.removeToken(address)

    def raw_transfer_owner_ship(self, address):
        return self._functions.transferOwnership(address)

    def raw_transfer_payee_ship(self, address):
        return self._functions.transferPayeeship(address)

    def raw_transfer_proof(self, token_address, datas):
        return self._functions.transferProof(token_address, datas)

    def raw_unpause(self):
        return self._functions.unpause()

    def raw_update_token(self, name, address):
        return self._functions.updateToken(name, address)

    def contract_version(self):
        return self._functions.contractVersion().call()

    def owner(self):
        return self._functions.owner().call()

    def paused(sefl):
        return self._functions.paused().call()

    def payee(self):
        return self._functions.payee().call()

    def token_address(self, name):
        return self._functions.tokenAddress(name).call()

    def token_name(self, address):
        return self._functions.tokenName(address).call()

    def token_name_list(self):
        max_count = self._functions.tokenMaxCount().call()
        names = []
        for i in range(max_count):
            name = self._functions.validTokenNames(i).call()
            if name is not None and len(name) > 0:
                names.append(name)

        return names

    def proof_address(self):
        return self._functions.proofAddress().call()

    def __getattr__(self, name):
        print(f"calling {name}")

def test():
    import usdt_abi
    import vmp_main_abi
    import vmp_datas_abi
    import vmp_state_abi
    VLSMPROOF_MAIN_NAME = "vmpmain"
    VLSMPROOF_DATAS_NAME = "vmpdatas"
    VLSMPROOF_STATE_NAME = "vmpstate"
    contract_codes = {
        "usdt" : {"abi":usdt_abi.ABI, "bytecode":usdt_abi.BYTECODE, "token_type": "erc20", "address": usdt_abi.ADDRESS},
        VLSMPROOF_MAIN_NAME: {"abi": vmp_main_abi.ABI, "bytecode": vmp_main_abi.BYTECODE, "token_type": "main", "address":vmp_main_abi.ADDRESS},
        VLSMPROOF_DATAS_NAME: {"abi":vmp_datas_abi.ABI, "bytecode": vmp_datas_abi.BYTECODE, "token_type": "datas", "address":vmp_datas_abi.ADDRESS},
        VLSMPROOF_STATE_NAME: {"abi":vmp_state_abi.ABI, "bytecode": vmp_state_abi.BYTECODE, "token_type": "state", "address":vmp_state_abi.ADDRESS},
    }


    #host = "http://127.0.0.1:8545"
    host = "https://kovan.infura.io/v3/2645261bd8844d0c9ac042c84606502d"
    w3 = Web3(Web3.HTTPProvider(host))
    if not w3.isConnected():
        raise Exception("not connect {host}")
    else:
        print("connected parity")

    usdt_address = "0x6f08730da8e7de49a4064d2217c6b68d7e61e727"
    contract_address = "0xCb9b6D30E26d17Ce94A30Dd225dC336fC4536FE8"
    vmp = vlsmproofmainslot(w3.eth.contract(Web3.toChecksumAddress(contract_address), abi=contract_codes[VLSMPROOF_MAIN_NAME]["abi"]), "vlsmproof")

    account = "0x89fF4a850e39A132614dbE517F80603b4A96fa0A"
    account1_privkey = '05849aa606c43ef46e1d71381573221538caef578973fb26f9b889b382d568bd'
    account2 = "0x9382690D0B835b69FD9C0bc23EB772a0Ddb3613F"

    #update_proof_state(w3, vmp, account, account1_privkey)

    print(f'''
    block number: {w3.eth.blockNumber}
    syncing: {w3.eth.syncing}
    ''')

    print(f'''
contract info:
    contract name: {vmp.slot_name()}
    name: {vmp.name()}
    symbol:{vmp.symbol()}
    owner : {vmp.owner()}
    payee : {vmp.payee()} 
    proof address : {vmp.proof_address()} 
    block number: {w3.eth.blockNumber}
    syncing: {w3.eth.syncing}
    gasLimit: {w3.eth.getBlock("latest").get("gasLimit")}
    ''')

    
if __name__ == "__main__":
    test()
