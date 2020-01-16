#!/usr/bin/python3
import operator
import sys
import json
import os
sys.path.append(os.getcwd())
sys.path.append("{}/libra-client".format(os.getcwd()))
sys.path.append("..")
sys.path.append("../libra-client")
import libra
from libra import Client
from libra import WalletLibrary
from libra.json_print import json_print
import log
import log.logger
import traceback
import datetime
import sqlalchemy
import stmanage
import requests
import random
import comm
import comm.error
import comm.result
from comm.result import result, parse_except
from comm.error import error
from db.dbb2v import dbb2v
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from enum import Enum
from baseobject import baseobject
from violas.violasclient import violasclient
import redis
#module name
name="violasproof"

class violasproof(violasclient):
    def __init__(self, name, nodes):
        violasclient.__init__(self, name, nodes)

    def __del__(self):
        violasclient.__del__(self)

    def create_data_for_end(self, flag, dtype, tranid):
        return json.dumps({"flag": flag, "type":dtype, "tran_id":tranid, "state": "end"})

    def create_data_for_mark(self, flag, dtype, txid, sequence):
        return json.dumps({"flag": flag, "type":dtype, "txid":txid, "sequence":sequence})
            

