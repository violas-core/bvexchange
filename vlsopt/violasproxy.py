#!/usr/bin/python3
import operator
import sys
import json
import os
sys.path.append(os.getcwd())
sys.path.append("..")
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../lbviolasclient"))

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
        VIOLAS_ADDRESS_LEN 
        )

#from violas.client import Client
#from violas.wallet import Wallet
#from violas.client import Client
from lbviolasclient.violas_client.wallet_library import Wallet
from lbviolasclient.violas_client.client import Client

#module name
name="violasproxy"
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
                
                if len(address_dd[0]) not in VIOLAS_ADDRESS_LEN or \
                        len(address_dd[1]) not in VIOLAS_ADDRESS_LEN:
                        raise Exception(f"address is invalid. {mnemonic_num[i]}")
                wallet.replace_address(address_dd[0], address_dd[1])
                i = i + 1

        return wallet

    @property
    def child_count(self):
        return len(self.accounts)

class violasproxy(Client):
    def __init__(self):
        pass

    def clientname(self):
        return name

    @classmethod
    def connect(self, host, port = None, faucet_file = None, 
            timeout =30, debug = False, faucet_server = None, waypoint = None):
        url = host
        if "://" not in host:
            url = f"http://{host}"
        if port is not None:
            url += f":{port}"
        return self.new(url = url, faucet_file = faucet_file, faucet_server = faucet_server, waypoint = waypoint)

    def send_coin(self, sender_account, receiver_address, micro_coins, token_id=None, module_address=None, data=None, \
            auth_key_prefix=None, is_blocking=False, max_gas_amount=400_000, unit_price=0, txn_expiration=13, gas_token_id = None):
        return self.transfer_coin(sender_account = sender_account, receiver_address = receiver_address, micro_coins = micro_coins, \
                currency_code = token_id, currency_module_address = module_address, data = data, is_blocking = is_blocking, gas_currency_code = gas_token_id)

def main():
    #client = clientproxy.connect(host="52.27.228.84", port=40001)
    #json_print(client.get_latest_version())
    wallet = walletproxy.load("vwallet")
if __name__ == "__main__":
    main()
