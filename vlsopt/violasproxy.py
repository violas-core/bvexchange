#!/usr/bin/python3
import operator
import sys
import json
import os
sys.path.append(os.getcwd())
sys.path.append("..")
sys.path.append("../libviolas")
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../libviolas"))
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
from violas.wallet import Wallet
from violas.client import Client

#module name
name="violasproxy"

class walletproxy(Wallet):

    @classmethod
    def load(self, filename):
        return self.recover(filename)

    


class clientproxy(Client):
    def __init__(self):
        pass

    @classmethod
    def connect(self, host, port = None, faucet_file = None, timeout =30, debug = False):
        return self.new(host = host, port = port, faucet_file = faucet_file, timeout=timeout, debug = debug)

def main():
    #client = clientproxy.connect(host="52.27.228.84", port=40001)
    #json_print(client.get_latest_version())
    wallet = walletproxy.load("vwallet")
if __name__ == "__main__":
    main()
