#!/usr/bin/python3
import operator
import sys, os
import json
sys.path.append("..")
sys.path.append(os.getcwd())
import log
import hashlib
import traceback
import datetime
import sqlalchemy
import setting
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
from db.dbvfilter import dbvfilter
from violas_base import vbase

#module name
name="vfilter"

COINS = comm.values.COINS
#load logging
logger = log.logger.getLogger(name) 
    
class vfilter(vbase):
    def __init__(self, rconf, vnodes):
        vbase.__init__(self, rconf, vnodes)

    def __del__(self):
        vbase.__del__(self)


    def work(self):
        i = 0
        #init
        vclient = self._vclient
        dbclient = self._dbclient

        try:
            ret = vclient.get_latest_transaction_version();
            if ret.state != error.SUCCEED:
                return ret
                
            chain_latest_ver = ret.datas

            ret = dbclient.get_latest_filter_ver()
            if ret.state != error.SUCCEED:
                return ret
            db_latest_ver = ret.datas
                
            if db_latest_ver is None or len(db_latest_ver) == 0:
                db_latest_ver = '-1'
            i = int(db_latest_ver) + 1
    
            latest_saved_ver = str(dbclient.get_latest_saved_ver().datas)
            print(f"latest_saved_ver={latest_saved_ver} start version = {i}  step = {self.get_step()} chain_latest_ver = {chain_latest_ver} ")
            if i >= chain_latest_ver:
               return 
    
            ret = vclient.get_transactions(i, self.get_step(), True)
            if ret.state != error.SUCCEED:
                return ret
            for data in ret.datas:
                dict = data.to_json()
    
                #save to redis db
                value = json.dumps(dict)
                key = dict.get("version", 0)

                ret = dbclient.set_latest_filter_ver(key)
                if ret.state != error.SUCCEED:
                    return ret
    
                tran_filter = self.parse_tran(dict)
                if tran_filter.state != error.SUCCEED or \
                        tran_filter.datas.get("flag", None) == self.trantype.UNKOWN or \
                        not tran_filter.datas.get("tran_state", False):
                    continue

                ret = dbclient.set(key, value)
                if ret.state != error.SUCCEED:
                    return ret

                dbclient.set_latest_saved_ver(key)
                logger.debug(tran_filter.datas)
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        else:
            print("filter end")
        return ret
        
def works():
    try:
        pass
        filter = vfilter(setting.violas_filter.get("db_transactions", None), setting.violas_nodes)
        filter.set_step(setting.violas_filter.get("step", 1000))
        ret = filter.work()
    except Exception as e:
        ret = parse_except(e)
    return ret

if __name__ == "__main__":
    logger.debug(f"start {__file__}.{__name__}")
    works()
