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
import stmanage
import requests
import comm
import comm.error
import comm.result
import comm.values
from comm.result import result, parse_except
from comm.error import error
from enum import Enum
from db.dbvfilter import dbvfilter
from analysis.analysis_base import abase
#module name
name="vfilter"

COINS = comm.values.COINS
#load logging
    
class afilter(abase):
    def __init__(self, name = "vfilter", ttype = "violas", dtype = None, dbconf = None, nodes = None, chain="violas"):
        #db user dbvfilter
        abase.__init__(self, name, ttype, dtype, None, nodes, chain) #no-use defalut db
        if dbconf is not None:
            self._dbclient = dbvfilter(name, dbconf.get("host"), dbconf.get("port"), dbconf.get("db"), dbconf.get("password"))

    def __del__(self):
        abase.__del__(self)

    @classmethod
    def get_tran_data(self, data, isviolas = True):
        tran_data = data.to_json()
        if isinstance(tran_data, str):
            tran_data = json.loads(tran_data)

        if "token_id" not in tran_data:
            tran_data["token_id"] = data.get_currency_code()

        if "data" not in tran_data:
                tran_data["data"] = data.get_data()

        if tran_data["data"] is not None:
            try:
                tran_data["data"] = bytes.fromhex(tran_data["data"]).decode()
            except Exception as e:
                parse_except(e)

        #remove no-use key
        no_use = ["currency_code"]
        for key in no_use:
            if key in tran_data:
                tran_data.pop(key)

        return tran_data

    def is_target_tran(self, tran_data):
        ret = self.parse_tran(tran_data)

        if ret.state != error.SUCCEED or \
                ret.datas.get("flag", None) not in self.get_tran_types() or \
                ret.datas.get("type") == self.datatype.UNKOWN or \
                not ret.datas.get("tran_state", False):
                return False
        return True

    def start(self):
        i = 0
        #init
        try:
            self._logger.debug("start filter work")
            ret = self._vclient.get_latest_transaction_version();
            if ret.state != error.SUCCEED:
                return ret
                
            chain_latest_ver = ret.datas

            ret = self._dbclient.get_latest_filter_ver()
            if ret.state != error.SUCCEED:
                return ret
            start_version = self.get_start_version(ret.datas + 1)
    
            latest_saved_ver = self._dbclient.get_latest_saved_ver().datas
            
            self._logger.debug(f"start version = {start_version}  step = {self.get_step()} latest_saved_ver={latest_saved_ver} " +
                    f"chain_latest_ver = {chain_latest_ver} diff_count={chain_latest_ver - start_version}")
            if start_version > chain_latest_ver:
               return result(error.SUCCEED)
    
            ret = self._vclient.get_transactions(start_version, self.get_step(), True)
            if ret.state != error.SUCCEED:
                return ret

            for data in ret.datas:
                if self.work() == False:
                    break

                version = data.get_version()

                ret = self._dbclient.set_latest_filter_ver(version)
                if ret.state != error.SUCCEED:
                    return ret

                tran_data = self.get_tran_data(data, self.from_chain == "violas")   
                if self.is_target_tran(tran_data) == False:
                    continue

                self._logger.debug(f"found new transaction. version: {version}: {tran_data['data']}")
                #save to redis db
                ret = self._dbclient.set(version, json.dumps(tran_data))
                if ret.state != error.SUCCEED:
                    return ret
                self._dbclient.set_latest_saved_ver(version)
                self._logger.info(f"save transaction to db. version : {version}")
 
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        finally:
            self._logger.debug("end filter work")
        return ret
        
def works():
    try:
        stmanage.set_conf_env("../bvexchange.toml")
        #ttype: chain name. data's flag(violas/libra). ex. ttype = "violas"
        #dtype: save transaction's data type(vfilter/lfilter) . ex. dtype = "vfilter" 
        dtype = "vfilter"
        obj = afilter(name="vfilter", ttype="violas", \
                dbconf=stmanage.get_db(dtype), nodes=stmanage.get_violas_nodes(), chain="violas")
        obj.set_step(1)
        obj.set_min_valid_version(11205310)
        ret = obj.start()
        if ret.state != error.SUCCEED:
            print(ret.message)

    except Exception as e:
        ret = parse_except(e)
    return ret

if __name__ == "__main__":
    works()
