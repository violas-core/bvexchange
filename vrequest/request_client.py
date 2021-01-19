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
from analysis.analysis_proof_base  import aproofbase
proofstate = aproofbase.proofstate
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

    def filter_proof_datas(self, data):
        datas = {"address": data["sender"], \
                "amount":int(data["amount"]), \
                "sequence":int(data["sequence"]),  \
                "version":int(data["version"]), \
                "to_address":data["to_address"], \
                "tran_id":data["tran_id"], \
                "receiver":data.get("receiver"), \
                "times":data.get("times", 0), \
                "out_amount":data.get("out_amount", 0), \
                "opttype":data.get("opttype"), \
                "chain":data.get("chain"), \
                "token_id":data["token_id"]}
        return datas


    def get_transactions_for_state(self, state, address, mtype, start = -1, limit = 10):
        try:
            datas = []
            ret = self._rclient.get_transactions_for_state(state, address, mtype, start, limit)
            if ret.state != error.SUCCEED:
                return ret
            
            for data in ret.datas:
                datas.append(self.filter_proof_datas(data))

            self._logger.debug(f"count={len(datas)}")
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_transactions_for_start(self, address, mtype, start, limit = 10, excluded = None):
        return self.get_transactions_for_state(proofstate.START, address, mtype, start, limit)

    def get_transactions_for_cancel(self, address, mtype, start, limit = 10, excluded = None):
        return self.get_transactions_for_state(proofstate.CANCEL, address, mtype, start, limit)

    def get_transactions_for_end(self, address, mtype, start, limit = 10):
        return self.get_transactions_for_state(proofstate.END, address, mtype, start, limit)

    def get_transactions_for_stop(self, address, mtype, start, limit = 10):
        return self.get_transactions_for_state(proofstate.STOP, address, mtype, start, limit)

    def has_transaction(self, sender, module, toaddress, sequence, amount, version, receiver):
        return self._rclient.has_transaction(sender, module, toaddress, sequence, amount, version, receiver)

    def has_transaction_for_tranid(self, tranid):
        return self._rclient.has_transaction_for_tranid(tranid)

    def is_end(self, tran_id):
        return self._rclient.is_target_state(proofstate.END, tran_id)

    def is_stop(self, tran_id):
        return self._rclient.is_target_state(proofstate.STOP, tran_id)

    def is_cancel(self, tran_id):
        return self._rclient.is_target_state(proofstate.CANCEL, tran_id)

    def get_latest_saved_ver(self):
        return self._rclient.get_latest_saved_ver()

    def get_tran(self, version):
        return self._rclient.get(version)

    def get_tran_by_tranid(self, tranid):
        try:
            ret = self._rclient.get(tranid)
            if ret.state != error.SUCCEED:
                return ret
            
            if ret.datas is None:
                return result(error.ARG_INVALID)

            ret = self.get_tran(ret.datas)
            if ret.state != error.SUCCEED:
                return ret

            ret = result(error.SUCCEED, datas = self.filter_proof_datas(json.loads(ret.datas)))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def select(self, name):
        return self._rclient.select(name)

    def get_transaction_record(self, sender, flag, opttype = "swap", cursor = 0, match=None, limit = 10):
        return self._rclient.get_transaction_record(sender, flag.lower(), opttype.lower(), cursor, match, limit)

    def get_transaction_records(self, senders, opttype = "swap", cursor = 0, match=None, limit = 10):
        return self._rclient.get_transaction_records(senders, opttype.lower(), cursor, limit)

    def list_record_address_for_chain(self, chain, opttype = "swap", cursor = 0, limit = 10):
        return self._rclient.scan(cursor, f"*_{chain.lower()}_{opttype.lower()}", limit)

    def get_latest_chain_ver(self):
        return self._rclient.get_latest_chain_ver()

    def set_exec_points(self, key, point, prefix = None):
        return self._rclient.set_exec_points(self.create_point_key(key, prefix), point)

    def get_exec_points(self, key, prefix = None):
        return self._rclient.get_exec_points(self.create_point_key(key, prefix))
