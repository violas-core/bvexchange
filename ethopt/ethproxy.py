#!/usr/bin/python3
import operator
import sys
import json
import os
sys.path.append("..")
import log
import log.logger
import traceback
import datetime
import stmanage
import requests
import random
import comm
import comm.error
import comm.result
import comm.values
from comm import version
from comm.result import result, parse_except
from comm.error import error
from enum import Enum
from comm.functions import json_print
from vlsmproof import vlsmproofslot as vlsmproof

import web3
from web3 import Web3

#module name
name="ethproxy"

from usdt_abi import (
        USDT_ABI,
        USDT_BYTECODE
        )

from vlsmproof_abi import (
        VLSMPROOF_ABI,
        VLSMPROOF_BYTECODE
        )

contract_codes = {
        "usdt" : {"abi":USDT_ABI, "bytecode":USDT_BYTECODE, "token_type": "erc20"},
        "vlsmproof": {"abi":VLSMPROOF_ABI, "bytecode": VLSMPROOF_BYTECODE, "token_type": "vlsmproof"}
        }

class walletproxy():
    @classmethod
    def load(self, filename):
        ret = self.recover(filename)
        return ret

    @property
    def child_count(self):
        return len(self.accounts)

    def find_account_by_address_hex(self, address):
        for i in range(self.child_count):
            if self.accounts[i].address.hex == address:
                return (i, self.accounts[i])

        return (-1, None)


class ethproxy():

    tokens_address = {}
    def clientname(self):
        return name
    
    def __init__(self, host, port, chain_id = 42, *args, **kwargs):
        self._w3 = None
        setattr(self, "chain_id", chain_id)
        self.connect(host, port, *args, **kwargs)

    def connect(self, host, port = None, *args, **kwargs):
        url = host
        if "://" not in host:
            url = f"http://{host}"
        if port is not None:
            url += f":{port}"

        self._w3 = Web3(Web3.HTTPProvider(url))
        assert self._w3.isConnected(), f"connect {url} is failed."


    def load_contract(self, name, address):
        if name not in contract_codes:
            raise Exception(f"contract({name}) is invalid.")

        contract = contract_codes[name]
        setattr(self, name, self._w3.eth.contract(Web3.toChecksumAddress(address), abi=contract["abi"]))
        tokens_address[name] = address

    def token_address(self, name):
        return tokens_address[name]

    def is_connected(self):
        return self._w3.isConnected()
    
    def send_transaction(self, sender, private_key, calldata, nonce = None, gas = None, gas_price = None):
        if not gas:
            gas = slef._w3.eth.getTransactionCount(Web3.toChecksumAddress(sender))
        if not gas_price:
            gas_price = self._w3.eth.gasPrice
        if not nonce:
            nonce = self._w3.eth.getTransactionCount(Web3.toChecksumAddress(account))

        raw_tran = calldata.buildTransaction({
            "chainId": self.chain_id,
            "gas" : gas,
            "gasPrice": gas_price,
            "nonce" : nonce
            })

        signed_txn = self._w3.eth.account.sign_transaction(raw_tran, private_key=private_key)
        txhash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        return txhash


    def call_default(self, *args, **kwargs):
        print(f"no defined function(args = {args} kwargs = {kwargs})")

    def block_number(self):
        return self._w3.eth.blockNumber

    def get_balance(self, address, token_id, *args, **kwargs):
        return self.vlsmproof.balance(token_id, address)

    def get_balances(self, address, token_id, *args, **kwargs):
        token_name_list = self.vlsmproof.token_name_list()
        balances = {}
        for token_id in token_name_list:
            balances.update({token_name: self.get_balance(token_id, address)})

        return balances

    def get_sequence_number(self, address):
        return self.vlsmproof.proof_address_sequence(address)

    def get_account_transaction_version(self, address, sequence):
        return self.vlsmproof.proof_address_version(address, sequence)

    def get_latest_version(self):
        return self.vlsmproof.next_version()

    def get_transactions(self, start_version, limit, nouse = None):
        return self.vlsmproof.get_transactions(start_version, limit)

    def __getattr__(self, name):
        if name.startswith('__') and name.endswith('__'):
            # Python internal stuff
            raise AttributeError
        raise Exception(f"not defined function:{name}")
        #return self.call_default
        
    def __call__(self, *args, **kwargs):
        pass


def main():
    client = clientproxy.connect("https://client.testnet.libra.org")
    json_print(client.get_latest_version())
if __name__ == "__main__":
    main()