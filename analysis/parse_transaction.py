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
from comm.values import trantypebase as trantype, datatypebase as datatype
from comm.result import result, parse_except
from comm.error import error

def parse_tran_type(flag):
    try:
        if flag is None or len(flag) == 0:
            return trantype.UNKOWN

        return trantype[flag.upper()]
    except Exception as e:
        parse_except(e)
    return trantype.UNKOWN

def parse_data_type(self, data):
    try:
        if data is None or len(data) == 0:
            return self.datatype.UNKOWN

        return datatype[data.upper()]
    except Exception as e:
        parse_except(e)
    return datatype.UNKOWN

def json_to_dict(data):
    try:
        data = json.loads(data)
        ret = result(error.SUCCEED, "", data)
    except Exception as e:
        ret = result(error.FAILED, "data is not json format.")
    return ret

def get_opttype_from_dtype(dtype):
    if dtype in [datatype.V2LM.value, datatype.L2VM.value, datatype.V2BM.value, datatype.B2VM.value]:
        return "map"
    else:
        return "swap"


def parse_tran(transaction):
    try:
        datas = {"flag"         : None, 
                "type"          : None, 
                "from_address"  : None,
                "to_address"    : None,
                "nettype"       : None,
                "state"         : None,
                "sequence"      : -1,
                "amount"        : 0,
                "sender"        : None,
                "receiver"      : None,
                "module"        : None,
                "token_id"      : 0,
                "token"         : None,
                "version"       : 0,
                "tran_id"       : None,
                "tran_state"    : False,
                "expiration_time": 0
                }

        ret = result(error.TRAN_INFO_INVALID, datas = datas)

        #check transaction state
        datas["version"]    =  transaction.get("version", 0)
        datas["tran_state"] =  transaction.get("success", False)
        if not datas["tran_state"]:
           return ret

        data = transaction.get("data")
        if data is None or len(data) == 0:
            return ret

        ret = json_to_dict(data)
        if ret.state != error.SUCCEED:
            return ret

        data_dict = ret.datas
        
        datas["flag"]           = data_dict.get("flag")
        datas["type"]           = data_dict.get("type")
        datas["from_address"]   = data_dict.get("from_address")
        datas["to_address"]     = data_dict.get("to_address")
        datas["times"]          = data_dict.get("times", 0)
        out_amount = data_dict.get("out_amount")
        if out_amount is None:
            out_amount = 0
        datas["out_amount"]     = int(out_amount)
        datas["out_amount_real"]= int(data_dict.get("out_amount_real", datas["out_amount"]))
        datas["nettype"]        = data_dict.get("nettype")
        datas["state"]          = data_dict.get("state")
        opttype = data_dict.get("opttype")
        if opttype is None:
            opttype = get_opttype_from_dtype(datas["type"])
        datas["opttype"]        = opttype
        datas["amount"]         = transaction.get("amount", 0)
        datas["sender"]         = transaction.get("sender")
        datas["receiver"]       = transaction.get("receiver")
        datas["token"]          = transaction.get("token_owner")
        datas["token_id"]       = transaction.get("token_id")
        datas["out_token"]      = transaction.get("out_token")
        datas["expiration_time"]= transaction.get("expiration_time", 0)
        datas["tran_id"]        = data_dict.get("tran_id")
        datas["sequence"]       = transaction.get("sequence_number")
        datas["module"]         = transaction.get("module_address")
        datas["confirm"]        = transaction.get("confirm", 1)
        datas["txid"]           = transaction.get("txid", "")

        ret = result(error.SUCCEED, datas = datas)
    except Exception as e:
        ret = parse_except(e, transaction)
    return ret

