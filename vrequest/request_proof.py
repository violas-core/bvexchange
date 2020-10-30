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
from analysis.analysis_proof_base  import aproofbase
proofstate = aproofbase.proofstate
#module name
name="requestproof"

class requestproof(requestbase):
    def __init__(self, name, host, port, db, passwd = None):
        requestbase.__init__(self, name, host, port, db, passwd)

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


    def has_transaction(self, tranid):
        try:
            ret = self.get(tranid)
            if ret.state != error.SUCCEED:
                return ret

            ret = result(error.SUCCEED, datas = True)
        except Exception as e:
            ret = parse_except(e)
        finally:
            self._logger.debug("end has_transaction.")
        return ret


    def get_transaction_record(self, sender, flag, opttype = "swap", cursor = 0, match = None, limit = 10):
        try:
            tran_info = {"flag":flag,"sender":sender, "opttype":opttype}
            
            name = self.create_haddress_name(tran_info)
            ret = self.hscan(name, cursor, match, limit)
            if ret.state != error.SUCCEED:
                return ret
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_transaction_records(self, senders, opttype = "swap", cursor = 0, limit = 10):
        try:
            hnames = []
            for sender in senders.split(","):
                hnames.append(f"{sender}_{opttype}")

            ret = self.get_records(opttype, hnames, cursor, limit)
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

    def is_target_state(self, state, tran_id):
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

def main():
    try:
        pass

    except Exception as e:
        parse_except(e)
    return ret

if __name__ == "__main__":
    main()
      
