#!/usr/bin/python3
import operator
import sys
import json
import os
sys.path.append(os.getcwd())
sys.path.append("..")
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
from vlsopt.violasclient import violasclient
import redis
#module name
name="violasproof"

class violasproof(violasclient):
    def __init__(self, name, nodes, chain="violas"):
        violasclient.__init__(self, name, nodes, chain)

    def __del__(self):
        violasclient.__del__(self)

    def create_data_for_start(self, flag, dtype, to_address):
        return json.dumps({"flag": flag, "type":dtype, "to_address":to_address, "state": "start"})

    def create_data_for_end(self, flag, dtype, tranid):
        return json.dumps({"flag": flag, "type":dtype, "tran_id":tranid, "state": "end"})

    def create_data_for_mark(self, flag, dtype, id, sequence):
        return json.dumps({"flag": flag, "type":dtype, "id":id, "sequence":sequence})
            

