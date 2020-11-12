#!/usr/bin/python3
import sys, getopt, os
import log 
import json

class dataproof():
    __datas = {}
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
        return self.__datas.update({chain:data})

    def __call__(self, *args, **kwargs):
        return self.get_wallet(args[0])

wallets = dataproof()
