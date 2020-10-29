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
from ethopt.vlsmproofslot import vlsmproofslot
from ethopt.erc20slot import erc20slot 
from ethopt.lbethwallet import lbethwallet

import web3
from web3 import Web3

#module name
name="ethproxy"

from usdt_abi import (
        USDT_ABI,
        USDT_BYTECODE,
        USDT_ADDRESS
        )

from vlsmproof_abi import (
        VLSMPROOF_ABI,
        VLSMPROOF_BYTECODE,
        VLSMPROOF_ADDRESS
        )
VLSMPROOF_NAME = "vlsmproof"
contract_codes = {
        "usdt" : {"abi":USDT_ABI, "bytecode":USDT_BYTECODE, "token_type": "erc20", "address": USDT_ADDRESS},
        VLSMPROOF_NAME: {"abi":VLSMPROOF_ABI, "bytecode": VLSMPROOF_BYTECODE, "token_type": "vlsmproof", "address":VLSMPROOF_ADDRESS}
        }

class walletproxy(lbethwallet):
    @classmethod
    def load(self, filename):
        ret = self.recover(filename)
        return ret

    def find_account_by_address_hex(self, address):
        for i in range(self.child_count):
            if self.accounts[i].address == address:
                return (i, self.accounts[i])

        return (-1, None)

    def __getattr__(self, name):
        if name.startswith('__') and name.endswith('__'):
            raise AttributeError

class ethproxy():

    class transaction:
        def __init__(self, data):
            self._data = dict(data)

        def to_json(self):
            return self._data

        def get_version(self):
            return self._data["version"]

        def get_data(self):
            return self._data["data"]

    def clientname(self):
        return name
    
    def __init__(self, host, port, chain_id = 42, *args, **kwargs):
        self._w3 = None
        self.tokens_address = {}
        self.tokens_decimals = {}
        self.tokens = {}
        self._vlsmproof_manager = None

        setattr(self, "chain_id", chain_id)
        self.connect(host, port, *args, **kwargs)
        self.load_vlsmproof(contract_codes[VLSMPROOF_NAME]["address"]) #default, config will override

    def connect(self, host, port = None, *args, **kwargs):
        url = host
        if "://" not in host:
            url = f"http://{host}"
            if port is not None:
                url += f":{port}"

        self._w3 = Web3(Web3.HTTPProvider(url))
        assert self._w3.isConnected(), f"connect {url} is failed."


    def load_vlsmproof(self, address):
        contract = contract_codes[VLSMPROOF_NAME]
        setattr(self, VLSMPROOF_NAME, vlsmproofslot(self._w3.eth.contract(Web3.toChecksumAddress(address), abi=contract["abi"])))
        self.tokens_address[VLSMPROOF_NAME] = address

    def load_contract(self, name):
        if name not in contract_codes:
            raise Exception(f"contract({name}) is invalid.")

        if name in VLSMPROOF_NAME:
            return

        contract = contract_codes[name]
        address = self.vlsmproof.token_address(name)
        assert contract is not None, f"not support token({name})"
        erc20_token = erc20slot(self._w3.eth.contract(Web3.toChecksumAddress(address), abi=contract["abi"]))
        setattr(self, name, erc20_token)
        self.tokens_address[name] = address
        self.tokens_decimals[name] = pow(10, erc20_token.decimals())
        self.tokens[name] = erc20_token

    def set_vlsmproof_manager(self, address):
        self._vlsmproof_manager = address

    def get_vlsmproof_manager(self, default = None):
        return self._vlsmproof_manager if self._vlsmproof_manager is not None else default

    def token_address(self, name):
        return self.tokens_address[name]

    def is_connected(self):
        return self._w3.isConnected()
    
    def syncing_state(self):
        return self._w3.eth.syncing

    def get_decimals(self, token):
        return self.tokens_decimals[token]

    def send_token(self, account, to_address, amount, token_id, nonce = None):
        calldata = self.tokens[token_id].transfer(to_address, amount)
        return self.send_transaction(account.address, account.key.hex(), callable, nonce = nonce) 

    def update_proof_state(self, from_address, version, state):
        calldata = self.vlsmproof.raw_transfer_proof_state_with_version(version, state)
        return self.send_transaction(account.address, account.key, callable, nonce = version) 

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
        return self.tokens[token_id].balanceOf(address)

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

    def create_std_metadata(self, datas):
        create = datas[6]
        metadata = {
                    "flag": "ethereum",
                    "type": f"e2vm",
                    "state": self.vlsmproof.state_name(datas[2]),
                    "opttype":"map",
                    "create" : create,
                    }
        if create:
            metadata.update({"to_address":datas[0], "out_amount": datas[5], "times":0})
        else:
            metadata.update({"tran_id":f"{datas[4]}_{datas[1]}"})
        return metadata

    def get_transactions(self, start, limit = 10, *args, **kwargs):
        return self._get_transactions(start, limit)

    def _get_transactions(self, start, limit = 10):
        next_version = self.vlsmproof.next_version()
        assert start >= 0 and start < next_version and limit >= 1, "arguments is invalid"
        datas = []
        end = start + limit
        end = min(end - 1, next_version - 1)
        payee = self.vlsmproof.payee()
        while start <= end:
            metadata = self.vlsmproof.proof_info_with_version(start)
            data = self.create_std_metadata(metadata)
            datas.append(self.transaction(
                {
                    "token_id": self.vlsmproof.token_name(metadata[3]),
                    "sender": metadata[4],
                    "receiver":self.get_vlsmproof_manager(payee),
                    "amount": metadata[5],
                    "token_owner": metadata[3],
                    "sequence_number":metadata[1],
                    "version":start,
                    "data" : json.dumps(data).encode("utf-8").hex(),
                    "success" : True,
                    }
                ))
            start += 1
        return datas

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
