#!/usr/bin/python3
import operator
import sys, os
import json
sys.path.append(os.getcwd())
sys.path.append("..")
import log
import log.logger

from vlsopt.violasclient import violasclient
from vlsopt.violasproof import violasproof
from ethopt.ethclient import ethclient
from btc.btcclient import btcclient
from comm.values import trantypebase as trantype
from baseobject import baseobject
from dataproof import dataproof

class clientfactory(baseobject):
    def __init__(self):
        baseobject.__init__(self, name)

    @classmethod
    def create(cls, name, chain, nodes):
       if chain == trantype.BTC.value:
           return btcclient(name, nodes) if nodes else None
       elif chain == trantype.VIOLAS.value:
           return violasproof(name, nodes, chain) if nodes else None
       elif chain == trantype.LIBRA.value:
           return violasproof(name, nodes, chain) if nodes else None
       elif chain == trantype.ETHEREUM.value:
           return ethclient(name, nodes, chain, usd_chain = dataproof.configs("eth_usd_chain")) if nodes else None
       
       raise Exception(f"create client failed. chain name({chain}) is invalid.")

    
