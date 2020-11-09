#!/usr/bin/python3

import sys, os, time
import json
sys.path.append(os.getcwd())
sys.path.append(f"..")

import web3
from web3 import Web3

class vlsmproofstateslot():

    def __init__(self, contract, name = "vlsmproofstate"):
        self._contract = contract
        self._name = name
        self._functions = contract.functions

    def slot_name(self):
        return self._name

    def name(self):
        return self._functions.name().call()

    def symbol(self):
        return self._functions.symbol().call()

    def state_name(self, value):
        return self._functions.getStateName(value).call()

    def state_value(self, name):
        return self._functions.getStateValue(name).call()

    def max_state_value(self):
        return self._functions.maxStateValue().call()

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
    contract_address = "0x93b774a66a37a9FfEE6Bc39760B1693B90356AF8"
    vmp = vlsmproofstateslot(w3.eth.contract(Web3.toChecksumAddress(contract_address), abi=contract_codes[VLSMPROOF_STATE_NAME]["abi"]), "vlsmproof")

    max_value = vmp.max_state_value()
    print(f"max state value: {max_value}")
    for i in range(max_value):
        print(f"state_name({i}):{vmp.state_name(i)}")

    print(f"state_name(1)->start:{vmp.state_name(1)}")

    
if __name__ == "__main__":
    test()
