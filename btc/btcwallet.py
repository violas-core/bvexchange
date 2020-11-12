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
    class Account:
        class Address:
            def __init__(self, value):
                self.value = value

            def hex(self):
                return self.value

        def __init__(self, address):
            self.__address = self.Address(address)

        @property
        def address(self):
            return self.__address

    def __init__(self, name, wallet= "bwallet"):
        baseobject.__init__(self, name)
        self.__wallet_info = {}
        if wallet is not None:
            self.loads(wallet)
        
    def loads(self, wallet):
        self.wallet_info.clear()
        if isinstance(wallet, dict):
            self.wallet_info = wallet
        elif os.path.isfile(wallet):
            with open(wallet) as lines:
                infos = lines.readlines()
                for info in infos:
                    info = info.strip("\n")
                    info = info.strip("\r")
                    items = info.split(",")
                    if len(items) != 3:
                        continue
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

    def get_account(self, address):
        try:
            ret = result(error.SUCCEED, datas = address)
        except Exception as e:
            ret = parse_except(e)
        return ret
         
def test_wallet():
    bwallet = btcwallet(name, "bwallet")
    bwallet.show_wallet_info()

if __name__ == "__main__":
    test_wallet()
