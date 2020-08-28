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
from comm.values import trantypebase, datatypebase
from comm.result import result, parse_except
from comm.error import error
from vlsopt.violasclient import violasclient, violaswallet, violasserver
from btc.btcclient import btcclient
from enum import Enum
from db.dbvbase import dbvbase
from baseobject import baseobject
from analysis.analysis_record import record
import analysis.parse_transaction as ptran
#module name
name="abase"

COINS = comm.values.COINS
class abase(baseobject):
    #enum name must be transaction datas "type"
    datatype = datatypebase
    trantype = trantypebase

    def __init__(self, name, ttype = None, dtype = None, dbconf = None, vnodes = None, chain="violas"):
        baseobject.__init__(self, name)
        self._step = 1000
        self.__dtypes = []
        self._tran_types = []
        self._min_valid_version = -1
        self._vclient = None
        self._dbclient = None
        self._rdbclient = None
        self._connect_db(name, dbconf)
        self._token_id = None
        self._vclient = None
        if chain == "btc":
            self._connect_btc(name, vnodes, chain)
        else:
            self._connect_violas(name, vnodes, chain)
        self.from_chain = chain

        self.append_data_type(dtype)
        self.append_tran_type(ttype)
        pass

    def __del__(self):
        if self._dbclient is not None:
            self._dbclient.save()

    def _connect_db(self, name, rconf):
        self._dbclient = None
        if rconf is not None:
            self._dbclient = dbvbase(name, rconf.get("host"), \
                    rconf.get("port"), \
                    rconf.get("db"), \
                    rconf.get("password"))
        return self._dbclient

    def _connect_violas(self, name, vnodes, chain="violas"):
        if vnodes is not None:
            self._vclient = violasclient(name, vnodes, chain) 
        return self._vclient

    def _connect_btc(self, name, node, chain="btc"):
        if node is not None:
            self._vclient = btcclient(name, node) 
        return self._vclient

    def set_swap_owner(self, address):
        self._swap_owner = address
        if self.from_chain == "violas" and self._vclient:
            self._vclient.swap_set_owner_address(address)

    def set_swap_module(self, address):
        self._swap_module = address
        if self.from_chain == "violas" and self._vclient:
            self._vclient.swap_set_module_address(address)

    def set_record(self, rdbconf):
        self._rdbclient = record(self.name(), rdbconf)

    def can_record(self):
        return self._rdbclient is not None and self._rdbclient.can_record()

    def set_min_valid_version(self, version):
        self._min_valid_version = version

    def get_min_valid_version(self):
        return self._min_valid_version

    def get_start_version(self, version):
        return max(self.get_min_valid_version(), version)

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
        if ttype is not None:
            self._tran_types.append(self._trantype_name_to_type(ttype))

    def get_tran_types(self):
        return self._tran_types

    def append_data_type(self, dtype):
        if dtype is None:
            return None
            
        self.__dtypes.append(self._datatype_name_to_type(dtype))

    def get_data_types(self):
        return self.__dtypes

    def set_step(self, step):
        if step is None or step <= 0:
            return
        self._step = step

    def append_token_id(self, token_id):
        assert isinstance(token_id, str) or isinstance(token_id, list), f"token_id({token_id}) is not str."
        isstr = isinstance(token_id, str)
        if self._token_id is None:
            self._token_id = []

        if isstr:
            self._token_id.append(token_id) 
        else:
            self._token_id.extend(token_id)

    def is_valid_token_id(self, token_id):
        assert isinstance(token_id, str), f"token_id({token_id}) is not str."
        return self._token_id is None or token_id in self._token_id

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

    def create_tran_id(self, flag, dtype, sender, receiver, module, version):
        return hashlib.sha3_256(f"{flag}.{dtype}.{sender}.{receiver}.{module}.{version}".encode("UTF-8")).hexdigest()

    def json_to_dict(self, data):
        try:
            data = json.loads(data)
            ret = result(error.SUCCEED, "", data)
        except Exception as e:
            ret = result(error.FAILED, "data is not json format.")
        return ret

    def parse_tran(self, transaction):
        try:
            ret = ptran.parse_tran(transaction)
            if ret.state == error.TRAN_INFO_INVALID:
                #this transaction is not swap transaction, ignore it
                return result(error.SUCCEED, datas = ret.datas)
            elif ret.state != error.SUCCEED:
                return ret

            tran = ret.datas
            if not self.is_valid_flag(tran.get("flag", None)):
                return result(error.SUCCEED, datas = tran)
            
            tran["flag"] = self.parse_tran_type(tran.get("flag"))
            tran["type"] = self.parse_data_type(tran.get("type"))
            ret = result(error.SUCCEED, datas = tran)
        except Exception as e:
            ret = parse_except(e)
        return ret

        
