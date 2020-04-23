#!/usr/bin/python3
import operator
import sys
import json
import os
sys.path.append("..")
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../libra-client"))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../libra-client/libra_client"))
print(sys.path)
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
import libra_client
from libra_client import Wallet
from libra_client import Client
#module name
name="libraproxy"

class walletproxy(Wallet):
    def __init__(self):
        pass

class clientproxy(Client):

    @classmethod
    def connect(self, host, port = None, faucet_file = None, timeout =30, debug = False):
        url = host
        if "://" not in host:
            url = f"https://{host}"
        if port is not None:
            url += f":{port}"

        return self.new(url)



    

def main():
    client = clientproxy.connect("https://client.testnet.libra.org")
    json_print(client.get_latest_version())
if __name__ == "__main__":
    main()
