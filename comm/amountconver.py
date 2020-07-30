#!/usr/bin/python3
import operator
import sys, os
import json
from enum import Enum

class amountconver():
    class amounttype(Enum):
        VIOLAS = 1
        BTC    = 2
        SATOSHI = 3

    def __init__(self, value, atype = amounttype.VIOLAS):
        
        if atype == self.amounttype.VIOLAS:
            self.violas_amount = value
        elif atype == self.amounttype.BTC:
            self.btc_amount = value
        elif atype == self.amounttype.SATOSHI:
            self.satoshi_amount = value
        else:
            raise Exception(f"amount type{atype} is invalid.")
        

    #btc -> violas
    @property
    def rate(self):
        return 100

    @property
    def satoshi(self):
        return 100000000

    @property
    def violas_amount(self):
        return self.__amount

    @violas_amount.setter
    def libra_amount(self, value):
        self.__amount = value

    @property
    def libra_amount(self):
        return self.__amount

    @violas_amount.setter
    def violas_amount(self, value):
        self.__amount = value
    @property
    def btc_amount(self):
        return float(self.satoshi_amount) / self.satoshi

    @btc_amount.setter
    def btc_amount(self, value):
        self.violas_amount = value * self.satoshi / self.rate

    @property
    def satoshi_amount(self):
        return self.violas_amount * self.rate

    @satoshi_amount.setter
    def satoshi_amount(self, value):
        self.violas_amount = int(value / self.rate)

    def amount(self, chain):
        if chain == "violas":
            return self.violas_amount
        elif chain == "libra":
            return self.libra_amount
        elif chain == "btc":
            return self.btc_amount
        else:
            raise Exception(f"chain({chain}) is invalid.")
