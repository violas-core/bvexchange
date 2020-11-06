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
    
if __name__ == "__main__":
    test()
