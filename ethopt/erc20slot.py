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

    def decimas(self):
        return self._contract.functions.decimals().call()

    def totalSupply(self):
        return self._contract.functions.totalSupply.call()

    def balanceOf(self, owner):
        return self._contract.functions.balanceOf(Web3.toChecksumAddress(owner)).call()

    def approve(self, spender, value):
        return self._contract.functions.approve(Web3.toChecksumAddress(spender), value).call()

    def transfer(self, to, value):
        return self._contract.functions.transfer(to, value).call()

    def transferFrom(self, fom, to, value):
        return self._contract.functions.transferFrom(fom, to, value).call()

    def transferRaw(self, to, value):
        return self._contract.functions.transfer(to, value)

    def transferFromRaw(self, fom, to, value):
        return self._contract.functions.transferFrom(fom, to, value)

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

    host = "http://51.140.241.96:8545"
    w3 = Web3(Web3.HTTPProvider(host))
    if not w3.isConnected():
        raise Exception("not connect {host}")

    token_address = "0x6f08730da8e7de49a4064d2217c6b68d7e61e727"
    usdt = erc20slot(w3.eth.contract(Web3.toChecksumAddress(token_address), abi=contract_codes["usdt"]["abi"]), "usdt")

    print(usdt.name())
    account = "0x89fF4a850e39A132614dbE517F80603b4A96fa0A"
    account1_privkey = '05849aa606c43ef46e1d71381573221538caef578973fb26f9b889b382d568bd'
    #print(f"usdt balance:{usdt.balanceOf('0x89fF4a850e39A132614dbE517F80603b4A96fa0A')}")
    print(f"usdt balance({account}):{usdt.balanceOf(account)}")
    account2 = "0x9382690D0B835b69FD9C0bc23EB772a0Ddb3613F"
    print(f"usdt balance({account2}):{usdt.balanceOf(account2)}")

    nonce = w3.eth.getTransactionCount(Web3.toChecksumAddress(account))
    usdt_txn = usdt.transferRaw(account2, 1000000).buildTransaction({
        'chainId': 42, #kovan
        'gas':10000000,
        'gasPrice': Web3.toWei(6, 'gwei'),
        'nonce': nonce,
        })
    print(f"usdt_txn:{usdt_txn}")
    signed_txn = w3.eth.account.sign_transaction(usdt_txn, private_key=account1_privkey)
    print(f"tx hash:{w3.toHex(signed_txn.hash)}")
    print(f"tx rawtransaction:{w3.toHex(signed_txn.rawTransaction)}")
    txhash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    print(f"ret tx hash:{w3.toHex(txhash)}")

    #w3.eth.waitForTransactionReceipt(txhash)
    print(f"usdt balance({account2}):{usdt.balanceOf(account2)}")

    
if __name__ == "__main__":
    test()