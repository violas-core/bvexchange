#!/usr/bin/python3
import sys, getopt, os
import log 
import json

class dataproof():
    __datas = {}
    ADDRS_SPLIT = ","
    FIELD_SPLIT = ":"

    def __init__(self):
        print(f"init dataproof")
        self.__init_defalut()

    def __init_defalut(self):
        self.update_wallet("violas", "vwallet")
        self.update_wallet("ethereum", "ewallet")
        self.update_wallet("libra", "lwallet")
        self.update_wallet("btc", "bwallet")

    def get_wallet(self, chain):
        return self.__datas[chain]

    def update_wallet(self, chain, data):
        if chain.lower() == "btc":
            #set for address:privkey
            if data.find(self.ADDRS_SPLIT) > 0 or data.find(self.FIELD_SPLIT) > 0:
                datas = {}
                addrs = data.split(self.ADDRS_SPLIT)
                assert len(addrs) > 0, f"data({data}) format is invalid."
                for addr in addrs:
                    fields = addr.split(self.FIELD_SPLIT)
                    assert len(fields) == 2, f"{addr} format is invalid, format: <ADDRESS>:<PRIVKEY>"
                    datas.update({fields[0]:{"address":fields[0], "publickey":None, "privkey": fields[1]}})
                return self.__datas.update({chain:datas})
                
        return self.__datas.update({chain:data})

    def __call__(self, *args, **kwargs):
        return self.get_wallet(args[0])

wallets = dataproof()
