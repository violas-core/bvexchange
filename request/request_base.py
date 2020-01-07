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
from analysis.violas_base  import vproof
proofstate = vproof.proofstate
#module name
name="rbase"

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

    def get_transaction_for_start(self, start = -1, limit = 10):
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
            for version in (start_version ,max_version + 1):
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

                if tran_info.get("state") == proofstate.START.name.lower():
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
      
