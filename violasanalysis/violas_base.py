#!/usr/bin/python3
import operator
import sys, os
import json
sys.path.append("..")
sys.path.append(os.getcwd())
import log
import hashlib
import traceback
import datetime
import sqlalchemy
import setting
import requests
import comm
import comm.error
import comm.result
import comm.values
from comm.result import result, parse_except
from comm.error import error
from db.dbv2b import dbv2b
from violas.violasclient import violasclient, violaswallet, violasserver
from enum import Enum
from db.dbvbase import dbvbase

#module name
name="vbase"

COINS = comm.values.COINS
#load logging
logger = log.logger.getLogger(name) 
    
class vbase(object):
    _step = 1000
    class datatype(Enum):
        V2B = 1
        V2L = 2
        UNKOWN = 255

    class trantype(Enum):
        VIOLAS = 1
        UNKOWN = 255

    def __init__(self, rconf, vnodes):
        self._vclient = None
        self._dbclient = None
        self._connect_db(rconf)
        self._connect_violas(vnodes)

    def __del__(self):
        if self._vclient is not None:
            self._vclient.disconn_node()
        if self._dbclient is not None:
            self._dbclient.save()

    def _connect_db(self, rconf):
        if rconf is not None:
            self._dbclient = dbvbase(rconf.get("host", "127.0.0.1"), rconf.get("port", 6378), rconf.get("db", "violas_filter"), rconf.get("password", None))
        return self._dbclient

    def _connect_violas(self, vnodes):
        if vnodes is not None:
            self._vclient = violasclient(vnodes) 
        return self._vclient

    def set_step(self, step):
        if step is None or step <= 0:
            return
        self._step = step

    def get_step(self):
        return self._step

    def parse_data_type(self, data):
        if data is None or len(data) == 0:
            return self.datatype.UNKOWN
        '''
        if data.find("v2b") == 0:
            return self.datatype.V2B
        if data.find("v2l") == 0:
            return self.datatype.V2L
        '''

        for etype in self.datatype:
            if etype.name == data.upper():
                return etype

        return self.datatype.UNKOWN

    def is_valid_flag(self, flag):
        return self.parse_tran_type(flag) != self.trantype.UNKOWN
        
    def parse_tran_type(self, flag):
        if flag is None or len(flag) == 0:
            return self.trantype.UNKOWN
        if flag == comm.values.EX_DATA_FLAG:
            return self.trantype.VIOLAS
        return self.trantype.UNKOWN
    def create_tran_id(self, flag, dtype, sender, receiver, vtoken, version):
        return hashlib.sha3_256(f"{flag}.{dtype}.{sender}.{receiver}.{vtoken}.{version}".encode("UTF-8")).hexdigest()

    def parse_tran(self, transaction):
        try:
            datas = {"flag"         : self.trantype.UNKOWN, 
                    "type"          : self.datatype.UNKOWN, 
                    "btc_address"   : None,
                    "libra_address" : None,
                    "vtbc_address"  : None,
                    "nettype"       : None,
                    "state"         : None,
                    "amount"        : 0,
                    "sender"        : None,
                    "receiver"      : None,
                    "vtoken"        : None,
                    "version"       : 0,
                    "tran_id"       : None,
                    "tran_state"    : False
                    }

            tran = result(error.SUCCEED, datas = datas)
    
            #check transaction state
            datas["version"] =  transaction.get("version", 0)
            datas["tran_state"] = transaction.get("success", False)
            if not datas["tran_state"]:
               return tran 

            #must has event(data)
            events = transaction.get("events", None)
            if events is None or len(events) == 0:
               return tran
    

            if events is None or len(events) == 0:
               return tran

            event = events[0].get("event", None)
            if event is None or len(event) == 0:
                return tran
    
            
            data = event.get("data", None)
            if data is None or len(data) == 0:
                return tran

            data_dict = json.loads(data)
            if not self.is_valid_flag(data_dict.get("flag", None)):
                return tran
            
            datas["flag"]           = self.parse_tran_type(data_dict.get("flag", None))
            datas["type"]           = self.parse_data_type(data_dict.get("type", None))
            datas["btc_address"]    = data_dict.get("btc_address", None)
            datas["libra_address"]  = data_dict.get("libra_address", None)
            datas["vtbc_address"]   = data_dict.get("vtbc_address", None)
            datas["nettype"]        = data_dict.get("nettype", None)
            datas["state"]          = data_dict.get("state", None)
            datas["amount"]         = event.get("amount", 0)
            datas["sender"]         = event.get("sender", None)
            datas["receiver"]       = event.get("receiver", None)
            datas["vtoken"]         = event.get("receiver", None)
            tran_id = data_dict.get("tran_id", None)
            datas["tran_id"]        = tran_id

            ret = result(error.SUCCEED, datas = datas)
        except Exception as e:
            ret = parse_except(e, transaction)
        return ret

        
