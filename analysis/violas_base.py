#!/usr/bin/python3
import operator
import sys, os
import json
sys.path.append("..")
sys.path.append(os.getcwd())
import hashlib
import traceback
import datetime
import sqlalchemy
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
from baseobject import baseobject

#module name
name="vbase"

COINS = comm.values.COINS
class vbase(baseobject):
    _step = 1000
    _dtypes = []
    _tran_types = []
    class datatype(Enum):
        V2B = 1
        V2L = 2
        L2V = 3
        UNKOWN = 255

    class trantype(Enum):
        VIOLAS = 1
        LIBRA  = 2
        UNKOWN = 255

    def __init__(self, name, ttype, dtype, dbconf, vnodes):
        baseobject.__init__(self, name)
        self._vclient = None
        self._dbclient = None
        self._connect_db(name, dbconf)
        self._connect_violas(name, vnodes)
        self.append_data_type(dtype)
        self.append_tran_type(ttype)

    def __del__(self):
        if self._vclient is not None:
            self._vclient.disconn_node()
        if self._dbclient is not None:
            self._dbclient.save()

    def _connect_db(self, name, rconf):
        if rconf is not None:
            self._dbclient = dbvbase(name, rconf.get("host", "127.0.0.1"), rconf.get("port", 6378), rconf.get("db"), rconf.get("password", None))
        return self._dbclient

    def _connect_violas(self, name, vnodes):
        if vnodes is not None:
            self._vclient = violasclient(name, vnodes) 
        return self._vclient

    def _datatype_name_to_type(self, name):
        for ev in self.datatype:
            if ev.name == name.upper():
                return ev
        raise ValueError(f"data type({name}) unkown")

    def _trantype_name_to_type(self, name):
        for ev in self.trantype:
            if ev.name == name.upper():
                return ev
        raise ValueError(f"tran type({name}) unkown")

    def stop(self):
        if self._vclient is not None:
            self._vclient.stop()
        self.work_stop()

    def append_tran_type(self, ttype):
        self._tran_types.append(self._trantype_name_to_type(ttype))

    def get_tran_types(self):
        return self._tran_types

    def append_data_type(self, dtype):
        if dtype is None:
            return None
            
        self._dtypes.append(self._datatype_name_to_type(dtype))

    def get_data_types(self):
        return self._dtypes

    def set_step(self, step):
        if step is None or step <= 0:
            return
        self._step = step

    def get_step(self):
        return self._step

    def parse_data_type(self, data):
        if data is None or len(data) == 0:
            return self.datatype.UNKOWN

        for etype in self.datatype:
            if etype.name == data.upper():
                return etype

        return self.datatype.UNKOWN

    def is_valid_flag(self, flag):
        return self.parse_tran_type(flag) in self._tran_types
        
    def parse_tran_type(self, flag):
        try:
            if flag is None or len(flag) == 0:
                return self.trantype.UNKOWN

            return self._trantype_name_to_type(flag)
        except Exception as e:
            parse_except(e)
        return self.trantype.UNKOWN

    def create_tran_id(self, flag, dtype, sender, receiver, vtoken, version):
        return hashlib.sha3_256(f"{flag}.{dtype}.{sender}.{receiver}.{vtoken}.{version}".encode("UTF-8")).hexdigest()

    def json_to_dict(self, data):
        try:
            data = json.loads(data)
            ret = result(error.SUCCEED, "", data)
        except Exception as e:
            ret = result(error.FAILED, "data is not json format.")
        return ret

    def parse_tran(self, transaction):
        try:
            datas = {"flag"         : self.trantype.UNKOWN, 
                    "type"          : self.datatype.UNKOWN, 
                    "btc_address"   : None,
                    "libra_address" : None,
                    "vtbc_address"  : None,
                    "nettype"       : None,
                    "state"         : None,
                    "sequence"      : -1,
                    "amount"        : 0,
                    "sender"        : None,
                    "receiver"      : None,
                    "token"         : None,
                    "version"       : 0,
                    "tran_id"       : None,
                    "tran_state"    : False
                    }

            tran = result(error.SUCCEED, datas = datas)
    
            #check transaction state
            datas["version"]    =  transaction.get("version", 0)
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

            ret = self.json_to_dict(data)
            if ret.state != error.SUCCEED:
                return tran

            data_dict = ret.datas
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
            datas["token"]          = event.get("token", None)
            tran_id = data_dict.get("tran_id", None)
            datas["tran_id"]        = tran_id
            datas["sequence"]   = transaction.get("raw_txn").get("sequence_number")

            ret = result(error.SUCCEED, datas = datas)
        except Exception as e:
            ret = parse_except(e, transaction)
        return ret

        
