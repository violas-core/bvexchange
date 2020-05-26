#!/usr/bin/python3
import operator
import sys, os
import json
sys.path.append(os.getcwd())
sys.path.append("..")
import log
import log.logger
import traceback
import datetime
import comm
import comm.error
import comm.result
import comm.values
from comm.functions import json_print
from comm.result import result, parse_except
from comm.error import error
from baseobject import baseobject
from enum import Enum

#module name
name="btcwallet"

class btcwallet(baseobject):
    def __init__(self, name, walletname = "bwallet"):
        baseobject.__init__(self, name)
        self.__wallet_info = {}
        self.loads(walletname)
        
    def loads(self, walletname):
        self.wallet_info.clear()
        with open(walletname) as lines:
            infos = lines.readlines()
            for info in infos:
                info = info.strip("\n")
                info = info.strip("\r")
                items = info.split(",")
                if len(items) != 3:
                    self._logger.warning("key info invalid:{info}")
                self.__wallet_info[items[0]]  = {"address":items[0], "publickey":items[1], "privkey":items[2]}

    @property 
    def wallet_info(self):
        return self.__wallet_info

    def address_is_exists(self, address):
        return address in self.wallet_info.keys()

    def get_publickey(self, address):
        info = self.wallet_info.get(address)
        if info is not None:
            return info.get("publickey")
        return None

    def get_privkey(self, address):
        info = self.wallet_info.get(address)
        if info is not None:
            return info.get("privkey")
        return None

    def show_wallet_info(self):
        json_print(self.wallet_info)
         
def test_wallet():
    bwallet = btcwallet(name, "bwallet")
    bwallet.show_wallet_info()

if __name__ == "__main__":
    test_wallet()