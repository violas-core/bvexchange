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

    def __init__(self, rconf):
        vbase.__init__(self, rconf, None)

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

            ret = self._dbclient.set_latest_filter_ver(version)

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

            #mark it, watch only
            self._dbclient.set_latest_saved_ver(version)
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret
        
