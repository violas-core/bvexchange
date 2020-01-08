#!/usr/bin/python3
'''
'''
import operator
import sys,os
import json
sys.path.append(os.getcwd())
sys.path.append("..")
import traceback
import datetime
import sqlalchemy
import stmanage
import random
import redis
import json
from comm.error import error
from comm.result import result, parse_except
from db.dbvproof import dbvproof

from enum import Enum
#module name
name="requestbase"

class requestbase(dbvproof):
    def __init__(self, name, host, port, db, passwd = None):
        dbvproof.__init__(self, name, host, port, db, passwd)
    
    def is_valid_tran(self, tran_info):
        try:
            pass
            ret = result(error.SUCCEED, "", True)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def _get_transaction_for_state(self, proofstate = None, receiver = None, module = None, start = -1, limit = 10):
        try:
            trans = []

            start_version = start
            if start < 0:
                ret = self.get_proof_min_version_for_start()
                if ret.state != error.SUCCEED:
                    return ret
                start_version = int(ret.datas)

            ret = self.get_latest_saved_ver()
            if ret.state != error.SUCCEED:
                return ret
            max_version = int(ret.datas)

            count = 0
            for version in range(start_version ,max_version + 1):
                if count >= limit:
                    break

                ret = self.key_is_exists(version)
                if ret.state != error.SUCCEED:
                    return ret

                if ret.datas == False:
                    continue

                ret = self.get(version)
                if ret.state != error.SUCCEED:
                    return ret

                tran_info = json.loads(ret.datas)
                ret = self.is_valid_tran(tran_info)
                if ret.state != error.SUCCEED:
                    return ret

                if ret.datas == False:
                    continue

                if proofstate is not None and tran_info.get("state") != proofstate.name.lower():
                    continue


                if receiver is not None and tran_info.get("receiver") != receiver:
                    continue

                if module is not None and tran_info.get("token") != module:
                    continue

                #data is valid, return it
                trans.append(tran_info)
                count += 1

            ret = result(error.SUCCEED, "", trans)
        except Exception as e:
            parse_except(e)
        return ret

def main():
    try:
        pass

    except Exception as e:
        parse_except(e)
    return ret

if __name__ == "__main__":
    main()
      
