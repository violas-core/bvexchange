#!/usr/bin/python3
import operator
import sys, os
import json
sys.path.append(os.getcwd())
sys.path.append("..")
import log
import log.logger

from vlsopt.violasclient import violaswallet 
from ethopt.ethclient import ethwallet
from btc.btcwallet import btcwallet
from comm.values import trantypebase as trantype
from baseobject import baseobject
from dataproof import dataproof

class walletfactory(baseobject):
    def __init__(self):
        baseobject.__init__(self, name)

    @classmethod
    def create(cls, name, chain)
       if chain == trantype.BTC.value:
           return btcwallet(name, dataproof.wallets(chain))
       elif chain == trantype.VIOLAS.value:
           return violaswallet(name, dataproof.wallets(chain), chain)
       elif chain == trantype.LIBRA.value:
           return violaswallet(name, dataproof.wallets(chain), chain)
       elif chain == trantype.ETHEREUM.value:
           return ethwallet(name, dataproof.wallets(chain))
       
       raise Exception(f"create wallet failed. chain name({chain}) is invalid.")

    
