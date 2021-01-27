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
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from enum import Enum
from baseobject import baseobject
from vlsopt.violasclient import violasclient
from comm.values import(
        datatypebase as datatype
        )
import redis
#module name
name="violasproof"

class violasproof(violasclient):
    def __init__(self, name, nodes, chain="violas", use_faucet_file = False):
        violasclient.__init__(self, name, nodes, chain, use_faucet_file = use_faucet_file)

    def __del__(self):
        violasclient.__del__(self)

    def __to_str_value(self, data):
        if not data:
            return data
        return data.value if not isinstance(data, str) else data

    def __flag_dtype_to_str(self, flag, dtype):
        return (self.__to_str_value(flag), self.__to_str_value(dtype))

    def create_data_for_start(self, flag, dtype, to_address, **kwargs):
        flag, dtype = self.__flag_dtype_to_str(flag, dtype)
        return json.dumps({"flag": flag, "type":dtype, "to_address":to_address, "state": "start"})

    def create_data_for_end(self, flag, dtype, tranid, txid="", **kwargs):
        flag, dtype = self.__flag_dtype_to_str(flag, dtype)
        datas = {"flag": flag, "type":dtype, "tran_id":tranid, "state": "end", "txid":txid, "out_amount_real": kwargs.get("out_amount_real", 0)}
        datas.update(kwargs)
        return json.dumps(datas)

    def create_data_for_stop(self, flag, dtype, tranid, txid="", **kwargs):
        flag, dtype = self.__flag_dtype_to_str(flag, dtype)
        return json.dumps({"flag": flag, "type":dtype, "tran_id":tranid, "state": "stop", "txid":txid})

    def create_data_for_cancel(self, flag, dtype, tranid, txid="", **kwargs):
        flag, dtype = self.__flag_dtype_to_str(flag, dtype)
        return json.dumps({"flag": flag, "type":dtype, "tran_id":tranid, "state": "cancel", "txid":txid})

    def create_data_for_mark(self, flag, dtype, id, version, **kwargs):
        flag, dtype = self.__flag_dtype_to_str(flag, dtype)
        return json.dumps({"flag": flag, "type":dtype + "_mark", "id":id, "version":version})
            
    def create_data_for_funds(self, flag, dtype, chain, tranid, tokenid, amount, to_address, **kwargs):
        '''
           @dev create funds request metadata
                note:  optype is liq or map, this server must be map
           @param dtype value is fixed  "funds"
           @param chain is request token's chain(violas btc libra ethereum)
           @param tranid is unique id
           @param tokenid is token name(violas:VLS BTC USDT  ethereum: usdt bitcoin: BTC)
           @param amount  microamount
           @param to_address receive token address
           @return metadata(json dumps)
        '''
        flag, dtype = self.__flag_dtype_to_str(flag, dtype)
        return json.dumps({"flag": flag, "type":dtype, "opttype": "map", "chain":chain, "tran_id":tranid, "token_id":tokenid ,"amount":amount, "to_address":to_address, "state":"start"})

    def create_data_for_msg(self, flag, opttype, token_id, amount, tranid, version, **kwargs):
        flag = self.__to_str_value(flag)
        opttype = self.__to_str_value(opttype)
        return json.dumps({"flag": flag, "type":datatype.MSG.value, "opttype": opttype, "token_id": token_id, "amount":amount, "tran_id":tranid, "version":version, "state":"start"})
            
