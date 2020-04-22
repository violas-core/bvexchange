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
from comm.error import error
from comm.result import result, parse_except
from enum import Enum
from vrequest.request_base import requestbase
from analysis.analysis_proof  import aproof
proofstate = aproof.proofstate
#module name
name="requestproof"

class requestproof(requestbase):
    def __init__(self, name, host, port, db, passwd = None):
        requestbase.__init__(self, name, host, port, db, passwd)
    
    def get_transactions_for_start(self, receiver = None, module = None, token_id = -1, start = -1, limit = 10):
        try:
            ret = self.get_proof_min_version_for_start()
            if ret.state == error.SUCCEED:
                start = max(start, int(ret.datas))

            self._logger.debug(f"get transactions for {proofstate.START.name}. receiver = {receiver} module={module} token_id = {token_id} start = {start} limit = {limit}")
            ret = self._get_transaction_for_state(proofstate.START, receiver, module, token_id, start, limit)
        except Exception as e:
            parse_except(e)
        return ret

    def get_transactions_for_end(self, receiver = None, module = None, token_id = -1, start = -1, limit = 10):
        try:
            ret = self._get_transaction_for_state(proofstate.END, receiver, module, token_id, start, limit)
        except Exception as e:
            parse_except(e)
        return ret

    def has_transaction_for_tranid(self, tranid):
        try:
            ret = self.get_proof_by_hash(tranid)
            if ret.state != error.SUCCEED:
                return ret

            tran_info = json.loads(ret.datas)
            beque = tran_info.get("tran_id") == tranid 
            ret = result(error.SUCCEED, "", beque)
        except Exception as e:
            ret = parse_except(e)
        finally:
            self._logger.debug("end has_transaction.")
        return ret


    def has_transaction(self, address, module, to_address, sequence, amount, version, receiver):
        try:
            ret = self.get(version)
            if ret.state != error.SUCCEED:
                return ret

            tran_info = json.loads(ret.datas)
            beque = tran_info.get("sender") == address and \
                    tran_info.get("module") == module and \
                    tran_info.get("to_address") == to_address and \
                    tran_info.get("sequence") == sequence and \
                    tran_info.get("amount") == amount and \
                    tran_info.get("version") == version and \
                    tran_info.get("receiver") == receiver

            ret = result(error.SUCCEED, "", beque)
        except Exception as e:
            ret = parse_except(e)
        finally:
            self._logger.debug("end has_transaction.")
        return ret

    def get_transaction_record(self, sender, flag, cursor = 0, match = None, limit = 10):
        try:
            tran_info = {"flag":flag,"sender":sender}
            
            name = self.create_haddress_name(tran_info)
            ret = self.hscan(name, cursor, match, limit)
            if ret.state != error.SUCCEED:
                return ret
        except Exception as e:
            ret = parse_except(e)
        return ret

    def list_keys_for_substr(self, substr, cursor = 0, limit = 10):
        try:
            ret = self.scan(cursor, sbustr, limit)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def _is_target_state(self, state, tran_id):
        try:
            ret = self.get_proof_by_hash(tran_id)
            if ret.state != error.SUCCEED:
                return ret

            tran_info = json.loads(ret.datas)
            beque = tran_info.get("tran_id") == tran_id and \
                    tran_info.get("state") == state.name.lower()

            ret = result(error.SUCCEED, "", beque)
        except Exception as e:
            ret = parse_except(e)

        return ret

    def is_start(self, tran_id):
        return self._is_target_state(proofstate.START, tran_id)

    def is_end(self, tran_id):
        return self._is_target_state(proofstate.END, tran_id)

def main():
    try:
        pass

    except Exception as e:
        parse_except(e)
    return ret

if __name__ == "__main__":
    main()
      
