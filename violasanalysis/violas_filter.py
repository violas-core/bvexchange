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
from violasanalysis.violas_base import vbase
from violasanalysis.violas_proof import vproof

#module name
name="vfilter"

COINS = comm.values.COINS
#load logging
logger = log.logger.getLogger(name) 
    
class vfilter(vbase):
    def __init__(self, vfconf, vnodes, vpconf):
        self._vclient = None
        self._dbclient = None
        self._connect_violas(vnodes)
        if vfconf is not None:
            self._dbclient = dbvfilter(vfconf.get("host", "127.0.0.1"), vfconf.get("port", 6378), vfconf.get("db", "violas_filter"), vfconf.get("password", None))
        self._vproof = vproof(vpconf)

    def __del__(self):
        vbase.__del__(self)


    def work(self):
        i = 0
        #init
        try:
            ret = self._vclient.get_latest_transaction_version();
            if ret.state != error.SUCCEED:
                return ret
                
            chain_latest_ver = ret.datas

            ret = self._dbclient.get_latest_filter_ver()
            if ret.state != error.SUCCEED:
                return ret
            db_latest_ver = ret.datas
                
            if db_latest_ver is None or len(db_latest_ver) == 0:
                db_latest_ver = '-1'
            i = int(db_latest_ver) + 1
    
            latest_saved_ver = str(self._dbclient.get_latest_saved_ver().datas)
            logger.debug(f"latest_saved_ver={latest_saved_ver} start version = {i}  step = {self.get_step()} chain_latest_ver = {chain_latest_ver} ")
            if i > chain_latest_ver:
               return result(error.SUCCEED)
    
            ret = self._vclient.get_transactions(i, self.get_step(), True)
            if ret.state != error.SUCCEED:
                return ret
            for data in ret.datas:
                dict = data.to_json()
    
                #save to redis db
                value = json.dumps(dict)
                key = dict.get("version", 0)

                ret = self._dbclient.set_latest_filter_ver(key)
                if ret.state != error.SUCCEED:
                    return ret
    
                ret = self.parse_tran(dict)
                if ret.state != error.SUCCEED or \
                        ret.datas.get("flag", None) == self.trantype.UNKOWN or \
                        not ret.datas.get("tran_state", False):
                    continue
                tran_filter = ret.datas
                logger.debug(f"transaction parse: {tran_filter}")

                ret = self._dbclient.set(key, value)
                if ret.state != error.SUCCEED:
                    return ret
                self._dbclient.set_latest_saved_ver(key)

                #this is target transaction, todo work here
                ret = self._vproof.update_proof_info(tran_filter)
                if ret.state != error.SUCCEED:
                    logger.error(ret.message)
 
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        else:
            print("filter end")
        return ret
        
def works():
    try:
        filter = vfilter(setting.violas_filter.get("db_transactions", None), setting.violas_nodes, setting.violas_filter.get("db_proof", None))
        filter.set_step(setting.violas_filter.get("step", 1000))
        ret = filter.work()
        if ret.state != error.SUCCEED:
            logger.error(ret.message)

    except Exception as e:
        ret = parse_except(e)
    return ret

if __name__ == "__main__":
    logger.debug(f"start {__file__}.{__name__}")
    works()
