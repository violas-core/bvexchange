#!/usr/bin/python3
import operator
import sys
import json
import os
sys.path.append("..")
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../lblibraclient"))
#sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../lblibraclient/libra_client"))
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
from comm.values import (
        VIOLAS_ADDRESS_LEN as LIBRA_ADDRESS_LEN
        )

#from violas.client import Client
from lblibraclient.libra_client import Wallet
from lblibraclient.libra_client import Client as LBRClient
from lblibraclient.libra_client.lbrtypes.chain_id import NamedChain
#module name
name="libraproxy"

ASSIGNMENT = "="
class walletproxy(Wallet):
    @classmethod
    def load(self, filename):
        if os.path.isfile(filename):
            self.__wallet_name = filename
            with open(filename) as lines:
                infos = lines.readlines()
                for info in infos:
                    return self.loads(info)


    @classmethod
    def loads(cls, data):
        mnemonic_num = data.split(Wallet.DELIMITER)
        if len(mnemonic_num) < 2 or not mnemonic_num[1].isdecimal():
            raise Exception(f"Format error: Wallet must <MNEMONIC_NUM>{Wallet.DELIMITER}<NUM>[ADDRESS{ASSIGNMENT}DD_ADDRESS;ADDRESS{ASSIGNMENT}DD_ADDRESS]")
        
        wallet = cls.new_from_mnemonic(mnemonic_num[0]) 
        wallet.generate_addresses(int(mnemonic_num[1]))
        if len(mnemonic_num) > 2:
            i = 2
            while i < len(mnemonic_num):
                address_dd = [value.strip() for value in mnemonic_num[i].split(ASSIGNMENT)]
                if len(address_dd) != 2:
                    raise Exception(f"address mapping format error: ADDRESS{ASSIGNMENT}DD_ADDRESS")
                
                if len(address_dd[0]) not in LIBRA_ADDRESS_LEN or \
                        len(address_dd[1]) not in LIBRA_ADDRESS_LEN:
                        raise Exception(f"address is invalid. {mnemonic_num[i]}")
                wallet.replace_address(address_dd[0], address_dd[1])
                i = i + 1

        return wallet

    @property
    def child_count(self):
        return len(self.accounts)

    def find_account_by_address_hex(self, address):
        for i in range(self.child_count):
            if self.accounts[i].address.hex == address:
                return (i, self.accounts[i])

        return (-1, None)


class libraproxy(LBRClient):
    def clientname(self):
        return name

    @classmethod
    def connect(self, host, port = None, faucet_file = None, timeout =30, debug = False):
        url = host
        if "://" not in host:
            url = f"http://{host}"
        if port is not None:
            url += f":{port}"

        return self.new(url, NamedChain.TESTNET)

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
