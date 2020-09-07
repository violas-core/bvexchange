#!/usr/bin/python3
import operator
import sys, os
import json
from enum import Enum

class amountconver():
    class amounttype(Enum):
        LIBRA  = 0
        VIOLAS = 1
        BTC    = 2
        SATOSHI = 3

    def __init__(self, value, atype = amounttype.VIOLAS):
        
        if atype in (self.amounttype.VIOLAS, self.amounttype.LIBRA):
            self.violas_amount = value
        elif atype == self.amounttype.BTC:
            if isinstance(value, int):
                self.satoshi_amount = value
            else:
                self.btc_amount = value
        elif atype == self.amounttype.SATOSHI:
            self.satoshi_amount = value
        else:
            raise Exception(f"amount type{atype} is invalid.")
        

    @property 
    def amount_type(self):
        return self.__amounttype

    @amount_type.setter
    def amount_type(self, value):
        self.__amounttype = value

    #btc -> violas
    @property
    def rate(self):
        return 100

    @property
    def satoshi(self):
        return 100000000

    @property
    def violas_amount(self):
        return int(self.__amount / self.rate)

    @violas_amount.setter
    def violas_amount(self, value):
        self.__amount = int(value * self.rate)

    @property
    def libra_amount(self):
        return int(self.__amount / self.rate)

    @libra_amount.setter
    def libra_amount(self, value):
        self.__amount = int(value * self.rate)

    @property
    def btc_amount(self):
        return float(self.satoshi_amount) / self.satoshi

    @btc_amount.setter
    def btc_amount(self, value):
        self.__amount = int(value * self.satoshi)

    @property
    def satoshi_amount(self):
        return self.__amount

    @satoshi_amount.setter
    def satoshi_amount(self, value):
        self.__amount = int(value)

    def amount(self, chain):
        if chain == "violas":
            return self.violas_amount
        elif chain == "libra":
            return self.libra_amount
        elif chain == "btc":
            return self.btc_amount
        else:
            raise Exception(f"chain({chain}) is invalid.")

    def microamount(self, chain):
        if chain == "violas":
            return self.violas_amount
        elif chain == "libra":
            return self.libra_amount
        elif chain == "btc":
            return self.satoshi_amount
        else:
            raise Exception(f"chain({chain}) is invalid.")
