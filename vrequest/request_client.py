#!/usr/bin/python3
'''
'''
import operator
import sys,os
import json
sys.path.append(os.getcwd())
sys.path.append("..")
import datetime
import stmanage
import random
import redis
import json
import vrequest
import vrequest.request_proof
from comm.error import error
from comm.result import result, parse_except
from enum import Enum
from vrequest.request_base import requestbase
from analysis.analysis_proof  import aproof
proofstate = aproof.proofstate
from vrequest.request_proof import requestproof
from baseobject import baseobject
#module name
name="requestclient"

class requestclient(baseobject):
    def __init__(self, name, dbconf):
        baseobject.__init__(self, name)
        try:
            self._rclient = requestproof(name, dbconf.get("host"), dbconf.get("port", 6378), dbconf.get("db"), dbconf.get("password"))
        except Exception as e:
            pass
    def get_transactions_for_start(self, address, module, start = -1, limit = 10):
        try:
            datas = []
            ret = self._rclient.get_transactions_for_start(address, module, start, limit)
            if ret.state != error.SUCCEED:
                return ret
            
            for data in ret.datas:
                version     = int(data["version"])
                address     = data["sender"]
                amount      = int(data["amount"])
                sequence    = int(data["sequence"])
                toaddress    = data["to_address"]
                tran_id     = data["tran_id"]
                datas.append({"address": address, "amount":amount, "sequence":sequence,  "version":version, "to_address":toaddress, "tran_id":tran_id})
            self._logger.debug(f"count={len(datas)}")
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        finally:
            self._logger.debug("end get_transactions_for_start.")
        return ret

    def get_transactions_for_end(self, address, module, start, limit = 10):
        try:
            datas = []
            ret = self._rclient.get_transactions_for_end(address, module, start, limit)
            if ret.state != error.SUCCEED:
                return ret
            
            for data in ret.datas:
                version     = int(data["version"])
                address     = data["sender"]
                amount      = int(data["amount"])
                sequence    = int(data["sequence"])
                baddress    = data["to_address"]
                tran_id     = data["tran_id"]
                datas.append({"address": address, "amount":amount, "sequence":sequence,  "version":version, "to_address":baddress, "tran_id":tran_id})
            self._logger.debug(f"count={len(datas)}")
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        finally:
            self._logger.debug("end get_transactions_for_end.")
        return ret
    def has_transaction(self, sender, module, toaddress, sequence, amount, version, receiver):
        try:
            self._logger.debug("start has_transaction(sender={}, module={}, toaddress={}, sequence={}, amount={}, version={}, receiver={})"\
                    .format(sender, module, toaddress, sequence, amount, version, receiver))
            ret = self._rclient.has_transaction(sender, module, toaddress, sequence, amount, version, receiver)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def has_transaction_for_tranid(self, tranid):
        try:
            self._logger.debug(f"start has_transaction_for_tranid({tranid})")
            ret = self._rclient.has_transaction_for_tranid(tranid)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def is_end(self, tran_id):
        return self._rclient.is_end(tran_id)

    def get_latest_saved_ver(self):
        return self._rclient.get_latest_saved_ver()

    def get_transaction_record(self, sender, module, cursor = 0, match=None, limit = 10):
        try:
            ret = self._rclient.get_transaction_record(sender, module, cursor, match, limit)
        except Exception as e:
            ret = parse_except(e)
        return ret
