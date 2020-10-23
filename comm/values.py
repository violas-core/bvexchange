#!/usr/bin/python3

import sys
from enum import Enum, auto

name="values"

COINS = 1000000  # map to satoshi/100
MIN_EST_GAS = 1000 * COINS / 100000000  #estimate min gas value(satoshi), check wallet address's balance is enough 

EX_TYPE_PROOF       = "proof"
EX_TYPE_PROOF_BASE  = "proofbase"
EX_TYPE_MARK        = "mark"
EX_TYPE_FIXTRAN     = "fixtran"

#token decimal btc and violas/libra is fixed  erc20 token ?
DECIMAL_VIOLAS  = 1_00_0000
DECIMAL_BTC     = 1_0000_0000

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
    VIOLAS      = auto()
    LIBRA       = auto()
    BTC         = auto()
    ETHEREUM    = auto()
    UNKOWN      = auto()

#datatype for transaction's data type
#parse metadata
class datatypebase(autoname):
    V2LM        = auto()
    L2VM        = auto()
    V2LUSD      = auto()
    V2LEUR      = auto()
    V2LSGD      = auto()
    V2LGBP      = auto()
    L2VUSD      = auto()
    L2VEUR      = auto()
    L2VSGD      = auto()
    L2VGBP      = auto()
    V2B         = auto()
    V2BM        = auto()
    B2VM        = auto()
    B2VUSD      = auto()
    B2VEUR      = auto()
    B2VSGD      = auto()
    B2VGBP      = auto()
    L2B         = auto()
    B2LUSD      = auto()
    B2LEUR      = auto()
    V2VSWAP     = auto()
    E2VM        = auto()
    V2EM        = auto()
    UNKOWN      = auto()

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


#work mod 
#workmod item(PROOF/EX) must be eq dbindexbase 
class workmod(enumbase):
    COMM         = auto()   
    VFILTER      = auto()    #scan violas chain
    LFILTER      = auto()
    BFILTER      = auto() #scan bitcoin chain
    EFILTER      = auto() #scan bitcoin chain
    V2VSWAPPROOF = auto() #scan violas chain swap
    #chain : libra ;  data source: lfilter ; result : transaction proof ; format : L2V + token_id + PROOF
    L2VMPROOF    = auto()
    L2VMEX       = auto()
    L2VUSDPROOF  = auto()
    L2VUSDEX     = auto()
    L2VEURPROOF  = auto()
    L2VEUREX     = auto()
    L2VGBPPROOF  = auto()
    L2VGBPEX     = auto()
    L2VSGDPROOF  = auto()
    L2VSGDEX     = auto()
    #chain : violas ; data source: vfilter ; result : transaction proof : fromat : V2L + token_id + PROOF
    V2LMPROOF    = auto()
    V2LMEX        = auto()
    V2LUSDPROOF  = auto()
    V2LUSDEX     = auto()
    V2LEURPROOF  = auto()
    V2LEUREX     = auto()
    #exchange : libra token id -> violas token id; format : L2V + token id + EX
    #exchange : violas token id -> libra token id; format : V2L + token id + EX
    #
    V2BPROOF     = auto()
    V2BEX        = auto()
    V2BMPROOF     = auto()
    V2BMEX        = auto()
    #
    B2VMPROOF     = auto()
    B2VMEX        = auto()
    B2VUSDPROOF  = auto()
    B2VUSDEX     = auto()
    B2VEURPROOF  = auto()
    B2VEUREX     = auto()
    B2VSGDPROOF  = auto()
    B2VSGDEX     = auto()
    B2VGBPPROOF  = auto()
    B2VGBPEX     = auto()
    #libran <-> btc
    #L2BPROOF     = auto()
    #L2BEX        = auto()
    #B2LUSDPROOF  = auto()
    #B2LUSDEX     = auto()
    #B2LEURPROOF  = auto()
    #B2LEUREX     = auto()
    E2VMPROOF  = auto()
    E2VMEX     = auto()
    V2EMPROOF  = auto()
    V2EMEX     = auto()

if __name__ == "__main__":
    print(dbindexbase.UNKOWN.info)
    print(workmod.COMM.info)
    print(workmod.LFILTER.info)
