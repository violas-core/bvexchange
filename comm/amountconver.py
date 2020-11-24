#!/usr/bin/python3
import operator
import sys, os
import json
sys.path.append(os.getcwd())
sys.path.append("..")

from enum import Enum
from comm.values import DECIMAL_VIOLAS, DECIMAL_BTC
class amountconver():
    class amounttype(Enum):
        LIBRA       = 0
        VIOLAS      = 1
        BTC         = 2
        ETHEREUM    = 3

    def __init__(self, value, atype = amounttype.VIOLAS, decimal = None):

        if atype in (self.amounttype.VIOLAS, self.amounttype.LIBRA):
            self.in_decimal = DECIMAL_VIOLAS
            self.micro_value = value
        elif atype == self.amounttype.BTC:
            self.in_decimal = DECIMAL_BTC
            self.micro_value = value
        elif atype == self.amounttype.ETHEREUM:
            self.in_decimal = decimal
            self.micro_value = value
        else:
            raise Exception(f"amount type{atype} is invalid.")

    @property 
    def amount_type(self):
        return self.__amounttype

    @amount_type.setter
    def amount_type(self, value):
        self.__amounttype = value

    #violas token decimal(1_0000_0000)
    @property
    def in_decimal(self):
        return self._in_decimal

    @in_decimal.setter
    def in_decimal(self, value):
        self._in_decimal = value

    def out_value_micro(self, out_decimal):
        assert self.in_decimal and out_decimal, \
                f"in_decimal: {self.in_decimal} and out_decimal: {out_decimal} is invalid."
        return int(float(self.micro_value * out_decimal) / self.in_decimal)

    def out_value_unit(self, out_decimal):
        assert self.in_decimal , \
                f"in_decimal: {self.in_decimal} is invalid."
        return float(self.micro_value) / self.in_decimal

    @property 
    def micro_value(self):
        return self.__amount

    @micro_value.setter
    def micro_value(self, value):
        if isinstance(value, int):
            self.__amount = value
        else:
            self.__amount = int(value * self.in_decimal)


    def amount(self, chain, decimal = None):
        chain = chain.lower()
        if chain in ("violas", "libra"):
            return self.out_value_micro(DECIMAL_VIOLAS)
        elif chain == "btc":
            return self.out_value_unit(DECIMAL_BTC)
        elif chain == "ethereum":
            return self.out_value_micro(decimal)
        else:
            raise Exception(f"chain({chain}) is invalid.")

    def microamount(self, chain, decimal = None):
        chain = chain.lower()
        if chain in ("violas", "libra"):
            return self.out_value_micro(DECIMAL_VIOLAS)
        elif chain == "btc":
            return self.out_value_micro(DECIMAL_BTC)
        elif chain == "ethereum":
            return self.out_value_micro(decimal)
        else:
            raise Exception(f"chain({chain}) is invalid.")

def MSG_TEXT(from_chain, amount, to_chain, target_amount, in_decimal = None, out_decimal = None):
    return f"{from_chain}({amount}) -> {to_chain}({target_amount}) in_decimal({in_decimal}, out_decimal({out_decimal}))" 

def CHECK_CONVER(from_chain, amount, to_chain, target_amount, in_decimal = None, out_decimal = None):
    msg = MSG_TEXT(from_chain, amount, to_chain, target_amount, in_decimal, out_decimal)
    assert amountconver(amount, amountconver.amounttype[from_chain], in_decimal).microamount(to_chain, out_decimal) == target_amount, f"{msg} failed"

    print(f"{msg} ok")

def CHECK_CONVER_UNIT(from_chain, amount, to_chain, target_amount, in_decimal = None, out_decimal = None):
    msg = MSG_TEXT(from_chain, amount, to_chain, target_amount, in_decimal, out_decimal)
    assert amountconver(amount, amountconver.amounttype[from_chain], in_decimal).amount(to_chain, out_decimal) == target_amount, f"{msg} failed"
    print(f"{msg} ok")
    

def test():
    CHECK_CONVER("BTC", 1_0000_0000, "violas", 1_00_0000)
    CHECK_CONVER_UNIT("BTC", 1_0000_0000, "btc", 1.0)
    CHECK_CONVER("BTC", 1_0000_0000, "libra", 1_00_0000)
    CHECK_CONVER("BTC", 1.0, "libra", 1_00_0000)
    CHECK_CONVER("BTC", 0.0000006, "libra", 0)
    CHECK_CONVER("BTC", 0.000001, "libra", 1)
    CHECK_CONVER("VIOLAS", 100_00_0000, "BTC", 100_0000_0000)
    CHECK_CONVER_UNIT("VIOLAS", 100_00_0000, "btc", 100.0)
    CHECK_CONVER("VIOLAS", 100_00_0000, "ethereum", 100_00_0000, out_decimal = 1_00_0000)
    CHECK_CONVER("VIOLAS", 100_00_0000, "ethereum", 100_00_0000, out_decimal = 1_00_0000)
    CHECK_CONVER("VIOLAS", 100_00_0000, "ethereum", 100_00_0000_0000, out_decimal = 1_00_0000_0000)
    CHECK_CONVER("BTC", 100_0000_0000, "ethereum", 100_00_0000_0000, out_decimal = 1_00_0000_0000)
    CHECK_CONVER("BTC", 100_0000_0000, "ethereum", 100_00_0000_0000_0000, out_decimal = 1_00_0000_0000_0000)
    CHECK_CONVER("BTC", 100_0000_0000, "ethereum", 100_00, out_decimal = 1_00)
    CHECK_CONVER("BTC", 1_0000_0000, "ethereum", 1_00, out_decimal = 1_00)
    CHECK_CONVER("BTC", 1_00_0000, "ethereum", 1, out_decimal = 1_00)
    CHECK_CONVER("BTC", 1_0_0000, "ethereum", 0, out_decimal = 1_00)
    

if __name__ == "__main__":
    test()
