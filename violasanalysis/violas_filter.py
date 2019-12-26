#!/usr/bin/python3
import operator
import sys, os
import json
sys.path.append("..")
sys.path.append(os.getcwd())
import log
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

#module name
name="vfilter"

COINS = comm.values.COINS
#load logging
logger = log.logger.getLogger(name) 
    
class vfilter:
    __step = 1000

    class datatype(Enum):
        V2B = 1
        V2L = 2
        UNKOWN = 255

    class trantype(Enum):
        VIOLAS = 1
        UNKOWN = 255

    def __init__(self, rconf, vnodes):
        self.__connect_db(rconf)
        self.__connect_violas(vnodes)

    def __del__(self):
        self.__vclient.disconn_node()

    def __connect_db(self, rconf):
        self.__dbclient = dbvfilter(rconf.get("host", "127.0.0.1"), rconf.get("port", 6378), rconf.get("db", "violas_filter"), rconf.get("password", None))
        return self.__dbclient

    def __connect_violas(self, vnodes):
        self.__vclient = violasclient(vnodes) 
        return self.__vclient

    def set_step(self, step):
        if step is None or step <= 0:
            return
        self.__step = step

    def get_step(self):
        return self.__step

    def parse_type(self, data):
        if data is None or len(data) == 0:
            return self.datatype.UNKOWN
        if data.find("v2b") == 0:
            return self.datatype.V2B
        if data.find("v2l") == 0:
            return self.datatype.V2L
        return self.datatype.UNKOWN

    def is_valid_flag(self, flag):
        return self.parse_tran_type(flag) != self.trantype.UNKOWN
        
    def parse_tran_type(self, flag):
        if flag is None or len(flag) == 0:
            return self.datatype.UNKOWN
        if flag == "violas":
            return self.trantype.VIOLAS
        return self.trantype.UNKOWN
        
    def parse_tran(self, transaction):
        try:
            datas = {"flag": self.trantype.UNKOWN, 
                    "type": self.datatype.UNKOWN, 
                    "btc_address": "",
                    "libra_address": "",
                    "vtbc_address": "",
                    "nettype":"",
                    "state":"",
                    "amount":0,
                    "sender":"",
                    "receiver":"",
                    "version":0,
                    }

            tran = result(error.SUCCEED, datas = datas)
            #must has event(data)
            events = transaction.get("events", None)
            if events is None or len(events) == 0:
               return tran
    
            event = events[0].get("event", None)
            if event is None or len(event) == 0:
                return tran
    
            
            data = event.get("data", None)
            if data is None or len(data) == 0:
                return tran

            data_dict = json.loads(data)
            if self.is_valid_flag(data_dict.get("flag", None)) == True:
                return tran
            
            datas["flag"] = self.parse_tran_type(data_dict.get("flag", None))
            datas["type"] = self.parse_type(data_dict.get("type", None))
            datas["btc_address"] = transaction.get("btc_address", None)
            datas["libra_address"] = data_dict.get("libra_address", None)
            datas["vtbc_address"] = data_dict.get("vtbc_address", None)
            datas["nettype"] = data_dict.get("nettype", None)
            datas["state"] = data_dict.get("state", None)
            ret = result(error.SUCCEED, datas = datas)
        except Exception as e:
            ret = parse_except(e)
        return ret


    def work(self):
        i = 0
        #init
        vclient = self.__vclient
        dbclient = self.__dbclient

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
                if tran_filter.state != error.SUCCEED or tran_filter.datas.get("flag") == self.trantype.UNKOWN:
                    continue

                ret = dbclient.set(key, value)
                if ret.state != error.SUCCEED:
                    return ret

                dbclient.set_latest_saved_ver(key)
                logger.debug(str(tran_filter))
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
