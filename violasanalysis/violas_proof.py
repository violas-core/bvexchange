#!/usr/bin/python3
import operator
import sys, os
import json
import math
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
from db.dbvproof import dbvproof
from violasanalysis.violas_base import vbase

#module name
name="vproof"

COINS = comm.values.COINS
#load logging
logger = log.logger.getLogger(name) 
    
class vproof(vbase):

    class proofstate(Enum):
        START = 1
        END = 2
        CANCEL = 3
        UNKOWN = 255

    def __init__(self, dbconf, vfdbconf, vnodes = None):
        self._vclient = None
        self._dbclient = None
        self._connect_violas(vnodes)
        self._dbclient = dbvproof(dbconf.get("host", "127.0.0.1"), dbconf.get("port", 6378), dbconf.get("db", "violas_vproof"), dbconf.get("password", None))
        self._vfdbcliet = dbvfilter(vfdbconf.get("host", "127.0.0.1"), vfdbconf.get("port", 6378), vfdbconf.get("db", "violas_vfilter"), vfdbconf.get("password", None))

    def __del__(self):
        vbase.__del__(self)

    def proofstate_name_to_value(self, name):
        if name is None or len(name) == 0:
            return self.proofstate.UNKOWN

        for estate in self.proofstate:
            if estate.name == name.upper():
                return estate

        return self.proofstate.UNKOWN

    def proofstate_value_to_name(self, value):
        for estate in self.proofstate:
            if estate == value:
                return estate.name.lower()
        return "unkown"

    def check_tran_is_valid(self, tran_info):
        return tran_info.get("flag", None) == self.trantype.VIOLAS and \
               self.proofstate_name_to_value(tran_info.get("state", "")) != self.proofstate.UNKOWN and \
               tran_info.get("type", self.datatype.UNKOWN) in (self.datatype.V2B, self.datatype.V2L)

    def update_proof_info(self, tran_info):
        try:
            logger.debug(f"start update_proof_info{tran_info}")
            version = tran_info.get("version", None)

            if self.check_tran_is_valid(tran_info) != True:
                return result(error.TRAN_INFO_INVALID, f"tran is valid(check flag type). violas tran info : {tran_info}")

            new_proof = False
            if self.proofstate_name_to_value(tran_info.get("state", "")) == self.proofstate.START:
                new_proof = True

            if new_proof == True:
                ret  = self._dbclient.key_is_exists(version)
                if ret.state != error.SUCCEED:
                    return ret

                #found key = version info, db has old datas , must be flush db?
                if ret.datas == True:
                    return result(error.TRAN_INFO_INVALID, f"key{version} is exists. violas tran info : {tran_info}")

                #create tran id
                tran_id = self.create_tran_id(tran_info["flag"], tran_info["type"], tran_info['sender'], \
                        tran_info['receiver'], tran_info['vtoken'], tran_info['version'])

                tran_info["flag"] = tran_info["flag"].name
                tran_info["type"] = tran_info["type"].name
                ret = self._dbclient.set(tran_id, version)
                ret = self._dbclient.set(version, json.dumps(tran_info))
                if ret.state != error.SUCCEED:
                    return ret

            else:
                tran_id = tran_info.get("tran_id", None)

                #get tran info from db(tran_id -> version -> tran info)
                ret = self._dbclient.get(tran_id)
                if ret.state != error.SUCCEED:
                    return ret

                version = ret.datas
                if version is None or len(version) == 0:
                    return result(error.TRAN_INFO_INVALID, f"update key{tran_id}, but not found, violas tran info : {tran_info}")


                ret = self._dbclient.get(version)
                if ret.state != error.SUCCEED:
                    return ret

                if ret.datas is None or len(ret.datas) == 0:
                    return result(error.TRAN_INFO_INVALID, f"key{version} not found value or key is not found.violas tran info : {tran_info}")

                db_tran_info = json.loads(ret.datas())

                #only recevier can change state (start -> end/cancel)
                if db_tran_info.get("receiver", "start state receiver") != tran_info.get("sender", "to end address"):
                    return result(error.TRAN_INFO_INVALID, f"violas info: {tran_info}\ndb info : {db_tran_info}") 

                #only db tran info's state = start, state can change
                if self.proofstate_name_to_value(db_tran_info.get("state", "")) != self.proofstate.START:
                    return result(error.TRAN_INFO_INVALID, f"db tran info : {db_tran_info}")

                db_tran_info["state"] = tran_info["state"]
                self._dbclient.set(version, db_tran_info)

            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret
        
    def work(self):
        try:
            logger.debug("start vproof work")
            ret = self._dbclient.get_latest_filter_ver()
            if ret.state != error.SUCCEED:
                return ret
            latest_filter_ver = ret.datas

            if latest_filter_ver is None or len(latest_filter_ver) == 0:
                latest_filter_ver = '-1'
            start_version = int(latest_filter_ver) + 1

            #can get max version 
            ret = self._vfdbcliet.get_latest_saved_ver()
            if ret.state != error.SUCCEED:
                return ret
            latest_saved_ver = ret.datas
            if latest_saved_ver is None or len(latest_saved_ver) == 0:
                latest_saved_ver = '-1'
            max_version = int(latest_saved_ver)

            #not found new transaction to change state
            if start_version > max_version:
                logger.debug(f"start version:{start_version} max version:{max_version}")
                return result(error.SUCCEED)

            version  = start_version
            count = 0
            logger.debug(f"proof latest_saved_ver={self._dbclient.get_latest_saved_ver()} start version = {start_version}  step = {self.get_step()} valid transaction latest_saved_ver = {latest_saved_ver} ")
            while(version <= max_version and count < self.get_step()):
                try:
                    #record last version(parse), maybe version is not exists
                    self._dbclient.set_latest_filter_ver(version)
                    logger.debug(f"parse transaction:{version}")

                    ret = self._vfdbcliet.get(version)
                    if ret.state != error.SUCCEED:
                        return ret

                    if ret.datas is None:
                        continue

                    tran_data = json.loads(ret.datas)
                    ret = self.parse_tran(tran_data)
                    if ret.state != error.SUCCEED or \
                            ret.datas.get("flag", None) == self.trantype.UNKOWN or \
                            not ret.datas.get("tran_state", False):
                        continue
                    tran_filter = ret.datas
                    logger.debug(f"transaction parse: {tran_filter}")

                    self._dbclient.set_latest_saved_ver(version)

                    #this is target transaction, todo work here
                    ret = self.update_proof_info(tran_filter)
                    if ret.state != error.SUCCEED:
                        logger.error(ret.message)

                    #mark it, watch only
                    self._dbclient.set_latest_saved_ver(version)
                    count += 1
                except Exception as e:
                    ret = parse_except(e)
                finally:
                    version += 1

        except Exception as e:
            ret = parse_except(e)
        finally:
            logger.debug("end vproof work")

        return ret

def works():
    try:
        _vproof = vproof(setting.violas_filter.get("db_vproof", None), setting.violas_filter.get("db_vfilter", None), setting.violas_nodes)
        _vproof.set_step(setting.violas_filter.get("db_vproof", "").get("step", 100))
        ret = _vproof.work()
        if ret.state != error.SUCCEED:
            logger.error(ret.message)

    except Exception as e:
        ret = parse_except(e)
    return ret
