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
    contract_codes = {
            "usdt" : {"abi":USDT_ABI, "bytecode":USDT_BYTECODE, "token_type": "erc20"},
            "vlsmproof": {"abi":VLSMPROOF_ABI, "bytecode": VLSMPROOF_BYTECODE, "token_type": "vlsmproof"}
            }


    def clientname(self):
        return name
    
    def __init__(self, host):
        self._w3 = None
        self._token = None

    def connect(self, host, port = None, faucet_file = None, timeout =30, debug = False):
        url = host
        if "://" not in host:
            url = f"http://{host}"
        if port is not None:
            url += f":{port}"

        self._w3 = Web3(Web3.HTTPProvider(url))

    def load_token(self, name, address):
        if name not in contract_codes:
            raise Exception(f"contract({name}) is invalid.")

        contract = contract_codes[name]
        setattr(self, name, self._w3.eth.contract(Web3.toChecksumAddress(address), abi=contract["abi"]))

    def name():

    def get_registered_currencies(self):
        pass


    def send_coin(self, sender_account, receiver_address, micro_coins, token_id=None, module_address=None, \
            data=None, auth_key_prefix=None, is_blocking=False, max_gas_amount=400_000, unit_price=0, txn_expiration=13):
        if data is not None:
            data = data.encode("utf-8")

        return self.transfer_coin(sender_account = sender_account, micro_coins = micro_coins, receiver_address=receiver_address, currency_code = token_id,\
                is_blocking = is_blocking, data = data, \
                max_gas_amount=max_gas_amount, gas_unit_price=unit_price)

    def get_account_sequence_number(self, address):
        return self.get_sequence_number(address)

    def call_default(self, *args, **kwargs):
        print(f"no defined function(args = {args} kwargs = {kwargs})")

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
