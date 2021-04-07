#!/usr/bin/python3

import sys, os
from enum import Enum, auto

name="values"

COINS = 1000000  # map to satoshi/100
MIN_EST_GAS = 1000 * COINS / 100000000  #estimate min gas value(satoshi), check wallet address's balance is enough 

PROJECT_NAME        = "violasbridge"
EX_TYPE_PROOF       = "proof"
EX_TYPE_PROOF_BASE  = "proofbase"
EX_TYPE_MARK        = "mark"
EX_TYPE_FIXTRAN     = "fixtran"

#token decimal btc and violas/libra is fixed  erc20 token ?
DECIMAL_VIOLAS  = 1_00_0000
DECIMAL_BTC     = 1_0000_0000

VIOLAS_ADDRESS_LEN = [32, 34, 64]
ETH_ADDRESS_LEN = [42]
BTC_ADDRESS_LEN = []

PACKAGE_ROOT_PATH = os.path.abspath(os.path.dirname(__file__)).split(os.path.dirname(__file__))[0]
class enumbase(Enum):
    @property
    def info(self):
        return f"{self.name}:{self.value}"

class autoname(enumbase):
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()

#transaction type for transaction's data flag
#parse metadata
class trantypebase(autoname):
    VIOLAS      = auto()
    LIBRA       = auto()
    DIEM        = auto()
    BTC         = auto()
    ETHEREUM    = auto()
    SMS         = auto()
    UNKOWN      = auto()

class langtype(autoname):
    CH      = auto()
    EN      = auto()

class msgtype(autoname):
    MINT    = auto()
    BURN    = auto()

'''
init chain dict for first char : chain name
'''
map_chain_name = {}
for ttb in trantypebase:
    name = ttb.name.lower()
    map_chain_name.update({name[:1]:name})

##db index(redis)
#dbindexbase item must be eq datatypebase item(B2Vxxx B2Lxxx L2Vxxx V2Lxxx)
class dbindexbase(enumbase):
    TEST    = 0
    RECORD  = 1
    #scan chain
    VFILTER = 2
    LFILTER = 3
    BFILTER = 4
    EFILTER = 5
    FUNDSVLS = 6
    MSG      = 7
    #proof datas
    V2LM    = 8
    L2VM    = 9
    V2LUSD  = 10
    V2LEUR  = 11
    V2LSGD  = 12
    V2LGBP  = 13
    L2VUSD  = 20
    L2VEUR  = 21
    L2VSGD  = 22
    L2VGBP  = 23
    V2B     = 30
    V2BM    = 31
    B2VM    = 32
    B2VUSD  = 36
    B2VEUR  = 37
    B2VSGD  = 38
    B2VGBP  = 39
    L2B     = 50
    B2LUSD  = 51
    B2LEUR  = 52
    V2VSWAP = 60
    E2VM   = 62
    V2EM   = 63

    '''
    funds spec type = FUNDS + TOKEN_ID
    append trantype item when want support new token id

    '''
    FUNDSBTC = 70
    FUNDSVBTC = 71
    FUNDSUSDT = 72
    FUNDSVUSDT = 73
    FUNDSWBTC = 74
    FUNDSVWBTC = 75

'''
filter chain type
'''
xfilter = ["VFILTER", "LFILTER","BFILTER", "EFILTER"]
dti_list = [item.name for item in dbindexbase if item.name not in ["TEST", "RECORD"]]

'''
merge enum item from names filters and ex args
@names is datatypebase name list
@filters : remove from names
@ex: append ex to then name end
'''
em_nv = lambda names, filters, ex = "" : \
        [(f"{name.upper()}{ex.upper()}", f"{name.lower()}{ex.lower()}") \
        for name in names \
        if filters is None or name.upper() not in filters]

#datatype for transaction's data type
#parse metadata
datatypebase = Enum("datatypebase",
        em_nv(dti_list + ["UNKOWN"], \
                xfilter, \
                str("") \
                ) \
        , module=__name__
        )

#work mod 
#workmod item(PROOF/EX) must be eq dbindexbase 
workmod = Enum("workmod", \
        em_nv(xfilter + ["COMM"], None, "") \
        + em_nv(dti_list, \
                xfilter, \
                str("PROOF") \
                ) \
        + em_nv(dti_list , \
                ["V2VSWAP"] + xfilter, \
                str("EX") \
                ) \
        , module=__name__
        )

if __name__ == "__main__":
    for item in workmod:
        print(f"{item.name} = {item.value}")
    
