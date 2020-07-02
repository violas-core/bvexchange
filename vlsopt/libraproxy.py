#!/usr/bin/python3
import operator
import sys
import json
import os
sys.path.append("..")
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../libra-client"))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../libra-client/libra_client"))
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

VIOLAS_ADDRESS_LEN = comm.values.VIOLAS_ADDRESS_LEN

#from violas.client import Client
from libra_client import Wallet
from libra_client import Client
#module name
name="libraproxy"

class walletproxy(Wallet):
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


class clientproxy(Client):
    @classmethod
    def connect(self, host, port = None, faucet_file = None, timeout =30, debug = False):
        url = host
        if "://" not in host:
            url = f"http://{host}"
        if port is not None:
            url += f":{port}"

        return self.new(url)

    def send_coin(self, sender_account, receiver_address, micro_coins, token_id=None, module_address=None, \
            data=None, auth_key_prefix=None, is_blocking=False, max_gas_amount=400_000, unit_price=0, txn_expiration=13):
        if data is not None:
            data = data.encode("utf-8")
        return self.transfer_coin(sender_account = sender_account, micro_coins = micro_coins, receiver_address=receiver_address, \
                is_blocking = is_blocking, data = data, receiver_auth_key_prefix_opt = auth_key_prefix, \
                max_gas_amount=max_gas_amount, gas_unit_price=unit_price)

    def get_account_sequence_number(self, address):
        return self.get_sequence_number(address)

    def swap_publish_contract(self, sender_account, is_blocking=True, **kwargs):
        pass

    def swap_add_currency(self, exchange_account, currency_code, is_blocking=True, **kwargs):
        pass

    def swap_add_liquidity(self, sender_account, currencyA, currencyB, amounta_desired, amountb_desired, amounta_min=None, amountb_min=None, is_blocking=True, **kwargs):
        pass

    def swap_initialize(self, module_account, is_blocking=True, **kwargs):
        pass

    def swap_remove_liquidity(self, sender_account, currencyA, currencyB, liquidity, amounta_min=0, amountb_min=0, is_blocking=True, **kwargs):
        pass

    def swap(self, sender_account, currency_in, currency_out, amount_in, amount_out_min=0, is_blocking=True, **kwargs):
        pass

def main():
    client = clientproxy.connect("https://client.testnet.libra.org")
    json_print(client.get_latest_version())
if __name__ == "__main__":
    main()
