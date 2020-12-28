#!/usr/bin/python3

import sys, os, time
sys.path.append(os.getcwd())
sys.path.append(f"..")

import web3
from web3 import Web3

class erc20slot():
    def __init__(self, contract, name = "erc20"):
        self._contract = contract
        self._name = name

    def slot_name():
        return self._name

    def name(self):
        return self._contract.functions.name().call()

    def symbol(self):
        return self._contract.functions.symbol().call()

    def decimals(self):
        return self._contract.functions.decimals().call()

    def totalSupply(self):
        return self._contract.functions.totalSupply.call()

    def balance_of(self, owner):
        return self._contract.functions.balanceOf(Web3.toChecksumAddress(owner)).call()

    def approve(self, spender, value):
        return self._contract.functions.approve(Web3.toChecksumAddress(spender), value).call()

    def allowance(self, owner, spender):
        return self._contract.functions.allowance(Web3.toChecksumAddress(owner), Web3.toChecksumAddress(spender)).call()

    def transfer(self, to, value):
        return self._contract.functions.transfer(to, value).call()

    def transfer_from(self, fom, to, value):
        return self._contract.functions.transferFrom(fom, to, value).call()

    def raw_transfer(self, to, value):
        return self._contract.functions.transfer(to, value)

    def raw_transfer_from(self, fom, to, value):
        return self._contract.functions.transferFrom(fom, to, value)

    def raw_approve(self, spender, value):
        return self._contract.functions.approve(Web3.toChecksumAddress(spender), value)

def test():

    host = "https://kovan.infura.io/v3/2645261bd8844d0c9ac042c84606502d"
    w3 = Web3(Web3.HTTPProvider(host))
    #if not w3.isConnected():
    #    raise Exception("not connect {host}")
    print("connect ok")
    print(f'''
    block number: {w3.eth.blockNumber}
    syncing: {w3.eth.syncing}
    ''')



    
if __name__ == "__main__":
    test()
