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

VIOLAS_ADDRESS_LEN = comm.values.VIOLAS_ADDRESS_LEN

#from violas.client import Client
#from violas.wallet import Wallet
#from violas.client import Client
from lbviolasclient.violas_client.wallet_library import Wallet
from lbviolasclient.violas_client.client import Client

#module name
name="violasproxy"

class walletproxy(Wallet):

    @classmethod
    def load(self, filename):
        return self.recover(filename)

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
            auth_key_prefix=None, is_blocking=False, max_gas_amount=400_000, unit_price=0, txn_expiration=13):
        return self.transfer_coin(sender_account = sender_account, receiver_address = receiver_address, micro_coins = micro_coins, \
                currency_code = token_id, currency_module_address = module_address, data = data, is_blocking = is_blocking)

def main():
    #client = clientproxy.connect(host="52.27.228.84", port=40001)
    #json_print(client.get_latest_version())
    wallet = walletproxy.load("vwallet")
if __name__ == "__main__":
    main()
