#!/usr/bin/python3
import operator
import sys
import json
import os
sys.path.append("..")
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../lbdiemsdk/src"))
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
from comm.values import (
        VIOLAS_ADDRESS_LEN as LIBRA_ADDRESS_LEN
        )

from vlsopt.proxybase import (
        proxybase
        )

from diem import (
    jsonrpc,
    diem_types,
    stdlib,
    testnet,
    utils,
    InvalidAccountAddressError,
    LocalAccount,
)

from vlsopt.data_factory import (
        account_factory,
        )
name="diemproxy"

class walletproxy(proxybase):
    ADDRESS_LEN = LIBRA_ADDRESS_LEN

    @property
    def name(self):
        return name

    @property
    def child_count(self):
        return len(self.accounts)

    def find_account_by_address_hex(self, address):
        for i in range(self.child_count):
            if self.accounts[i].address.hex == address:
                return (i, self.accounts[i])

        return (-1, None)



class diemproxy(jsonrpc.Client):
    def clientname(self):
        return name

    def __init__(self, url):
        jsonrpc.Client.__init__(self, url)

    @classmethod
    def connect(self, host, port = None, *args, **kwargs):
        url = host
        if "://" not in host:
            url = f"http://{host}"
        if port is not None:
            url += f":{port}"

        return diemproxy(url)

    def send_coin(self, sender_account, receiver_address, micro_coins, token_id=None, module_address=None, \
            data=None, auth_key_prefix=None, is_blocking=False, max_gas_amount=400_000, unit_price=0, txn_expiration=13, gas_token_id = None):
        if data is not None:
            data = data.encode("utf-8")

        return self.transfer_coin(sender_account = sender_account, micro_coins = micro_coins, receiver_address=receiver_address, currency_code = token_id,\
                is_blocking = is_blocking, data = data, \
                max_gas_amount=max_gas_amount, gas_unit_price=unit_price, gas_currency_code = gas_token_id)

    def get_account_sequence_number(self, address):
        return self.get_sequence_number(address)

    def call_default(self, *args, **kwargs):
        print(f"***no defined function(args = {args} kwargs = {kwargs})")

    def get_latest_version(self):
        metadata = self.get_metadata()
        state = self.get_last_known_state()
        return state.version

    def get_registered_currencies(self):
        currencies = self.get_currencies()
        return [currency.code for currency in currencies]

    def get_account_state(self, address):
        account = self.get_account(address)
        return account_factory(account)

    def get_balance(self, account_address, currency_code, *args, **kwargs):
        balances = self.get_balances(account_address)
        return balances.get(currency_code, 0)

    def get_balances(self, account_address, *args, **kwargs):
        account_state = self.get_account_state(account_address)
        return {balance.currency:balance.amount for balance in account_state.balances}

    def get_sequence_number(self, address):
        account_state = self.get_account_state(address)
        return account_state.sequence_number


    def __getattr__(self, name):
        try:
            if name.startswith('__') and name.endswith('__'):
                # Python internal stuff
                raise AttributeError
            return self.call_default
        except Exception as e:
            pass
        
        
    def __call__(self, *args, **kwargs):
        pass




def main():
    client = clientproxy.connect("https://client.testnet.libra.org")
    json_print(client.get_latest_version())
if __name__ == "__main__":
    main()
