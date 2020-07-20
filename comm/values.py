#!/usr/bin/python3

import sys
from enum import Enum, auto

name="values"

COINS = 1000000  # map to satoshi/100
MIN_EST_GAS = 1000 * COINS / 100000000  #estimate min gas value(satoshi), check wallet address's balance is enough 

EX_TYPE_B2V = "b2v"
EX_TYPE_B2L = "b2l"
EX_TYPE_V2B = "v2b"
EX_TYPE_PROOF = "proof"

VIOLAS_ADDRESS_LEN = [32, 64]

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
    VIOLAS = auto()
    LIBRA  = auto()
    BTC    = auto()
    UNKOWN = auto()

#datatype for transaction's data type
#parse metadata
class datatypebase(autoname):
    V2LUSD  = auto()
    V2LEUR  = auto()
    V2LSGD  = auto()
    V2LGBP  = auto()
    L2VUSD  = auto()
    L2VEUR  = auto()
    L2VSGD  = auto()
    L2VGBP  = auto()
    V2B     = auto()
    B2V     = auto()
    B2VUSD  = auto()
    B2VEUR  = auto()
    B2VSGD  = auto()
    B2VGBP  = auto()
    UNKOWN  = auto()

##db index(redis)
#dbindexbase item must be eq datatypebase item(B2Vxxx B2Lxxx L2Vxxx V2Lxxx)
class dbindexbase(enumbase):
    RECORD  = 1
    #scan chain
    VFILTER = 2
    LFILTER = 3
    BFILTER = 4
    #proof datas
    V2LUSD  = 10
    V2LEUR  = 11
    V2LSGD  = 12
    V2LGBP  = 13
    L2VUSD  = 20
    L2VEUR  = 21
    L2VSGD  = 22
    L2VGBP  = 23
    V2B     = 30
    B2V     = 35
    B2VUSD  = 36
    B2VEUR  = 37
    B2VSGD  = 38
    B2VGBP  = 39

#work mod 
#workmod item(PROOF/EX) must be eq dbindexbase 
class workmod(enumbase):
    COMM         = auto()   
    VFILTER      = auto()    #scan violas chain
    LFILTER      = auto()
    #chain : libra ;  data source: lfilter ; result : transaction proof ; format : L2V + token_id + PROOF
    L2VUSDPROOF  = auto()
    L2VEURPROOF  = auto()
    L2VGBPPROOF  = auto()
    L2VSGDPROOF  = auto()
    #chain : violas ; data source: vfilter ; result : transaction proof : fromat : V2L + token_id + PROOF
    V2LUSDPROOF  = auto()
    V2LEURPROOF  = auto()
    V2LGBPPROOF  = auto()
    V2LSGDPROOF  = auto()
    #exchange : libra token id -> violas token id; format : L2V + token id + EX
    L2VUSDEX     = auto()
    L2VEUREX     = auto()
    L2VGBPEX     = auto()
    L2VSGDEX     = auto()
    #exchange : violas token id -> libra token id; format : V2L + token id + EX
    V2LUSDEX     = auto()
    V2LEUREX     = auto()
    V2LGBPEX     = auto()
    V2LSGDEX     = auto()

    V2BPROOF     = auto()

    BFILTER      = auto() #scan bitcoin chain
    B2VPROOF     = auto()
    B2VEX        = auto()
    V2BEX        = auto()
    B2VUSDPROOF  = auto()
    B2VEURPROOF  = auto()
    B2VSGDPROOF  = auto()
    B2VGBPPROOF  = auto()
    B2VUSDEX     = auto()
    B2VEUREX     = auto()
    B2VSGDEX     = auto()
    B2VGBPEX     = auto()

if __name__ == "__main__":
    print(dbindexbase.UNKOWN.info)
    print(workmod.COMM.info)
    print(workmod.LFILTER.info)
