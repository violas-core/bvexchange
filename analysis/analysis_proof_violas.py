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
import stmanage
import requests
import comm
import comm.error
import comm.result
import comm.values
from comm.result import result, parse_except
from comm.error import error
from vlsopt.violasclient import violasclient, violaswallet, violasserver
from enum import Enum
from db.dbvfilter import dbvfilter
from db.dbvproof import dbvproof
from analysis.analysis_proof_base import aproofbase

#module name
name="aproofvls"
class aproofvls(aproofbase):

    def __init__(self, name = "vproof", 
            ttype = "violas",       #ttype violas/libra
            dtype = "vlsxxx",       #metadata  type:v2lxxx/l2vxxx
            dbconf = None,          #save analysis result db conf
            fdbconf = None,         #base data from lfilter/vfilter db conf
            rdbconf = None,         #save transaction record db conf 
            nodes = None,            #chain nodes libra/violas
            chain = "violas"
            ):
        super().__init__(name, ttype, dtype, dbconf, fdbconf, rdbconf, nodes, chain)

    def __del__(self):
        super().__del__()

    def stop(self):
        super().stop()

    def get_tran_id(self, tran_info):
        dtype = tran_info["type"]
        if stmanage.type_is_msg(dtype) or stmanage.type_is_funds(dtype):
            return tran_info["tran_id"]

        tran_id = self.create_tran_id(tran_info["flag"], tran_info["type"], tran_info['sender'], \
                tran_info['receiver'], tran_info['module'], tran_info['version']) 
        return tran_id

    def update_proof_info(self, tran_info):
        try:
            self._logger.debug(f"start update_proof_info tran info: {tran_info}")
            version = tran_info.get("version", None)

            tran_id = None
            new_proofstate = self.proofstate_name_to_value(tran_info.get("state", ""))

            new_proof = new_proofstate == self.proofstate.START

            self._logger.debug(f"new proof: {new_proof}")
            if new_proof:
                ret  = self._dbclient.key_is_exists(version)
                if ret.state != error.SUCCEED:
                    return ret
                found = ret.datas

                #create tran id
                tran_id = self.get_tran_id(tran_info)

                #found key = version info, db has old datas , must be flush db?
                if found: 
                    return result(error.TRAN_INFO_INVALID, f"key{version} tran_id({tran_id})is exists, db datas is old, flushdb ?. violas tran info : {tran_info}")

                tran_info["flag"] = tran_info["flag"].value
                tran_info["type"] = tran_info["type"].value
                tran_info["tran_id"] = tran_id

                ret = self._dbclient.set_proof(version, json.dumps(tran_info))
                if ret.state != error.SUCCEED:
                    return ret
                self._logger.info(f"saved new proof succeed. version = {tran_info.get('version')} tran_id = {tran_id} state={tran_info['state']}")

            else:
                tran_id = tran_info.get("tran_id", None)
                if tran_id is None or len(tran_id) == 0:
                    return result(error.TRAN_INFO_INVALID, f"new tran data info is invalid, tran info : {tran_info}")

                #get tran info from db(tran_id -> version -> tran info)

                ret = self._dbclient.get_proof_by_hash(tran_id)
                if ret.state != error.SUCCEED:
                    self._logger.debug(f"get_proof_by_hash({tran_id}) failed.")
                    return ret

                if ret.datas is None or len(ret.datas) == 0:
                    return result(error.TRAN_INFO_INVALID, 
                            f"tran_id {tran_id} not found value or key is not found.tran version : {tran_info.get('version')}")

                db_tran_info = json.loads(ret.datas)

                db_tran_id = db_tran_info.get("tran_id", None)
                if db_tran_id is None or len(db_tran_id) == 0 or db_tran_id != tran_id:
                    return result(error.TRAN_INFO_INVALID, f"new tran data info is invalid, tran version : {tran_info.get('version')}")

                old_proofstate = self.proofstate_name_to_value(db_tran_info.get("state", ""))
                if not self.is_valid_proofstate_change(new_proofstate, old_proofstate):
                    return result(error.TRAN_INFO_INVALID, f"change state to {new_proofstate.name} is invalid. \
                            old state is {old_proofstate.name}. tran version: {tran_info.get('version')}")

                #only recevier can change state 
                if not self.has_update_state_authority(new_proofstate, db_tran_info, tran_info):
                    return result(error.TRAN_INFO_INVALID, f"change state error. check transaction's sender is valid.") 

                db_tran_info["state"] = tran_info["state"]
                db_tran_info["out_amount_real"] = tran_info.get("out_amount_real", 0)
                self._dbclient.set_proof(db_tran_info.get("version"), json.dumps(db_tran_info))
                self._logger.info(f"change state succeed. version = {db_tran_info.get('version')} tran_id = {db_tran_id} state={db_tran_info['state']}")

            ret = result(error.SUCCEED, "", {"new_proof":new_proof, "tran_id":tran_id, "state": tran_info["state"]})
        except Exception as e:
            ret = parse_except(e)
        return ret

def works(ttype, dtype, basedata):
    try:
        #ttype: chain name. data's flag(violas/libra). ex. ttype = "violas"
        #dtype: save transaction's data type(v2b v2l l2v) . ex. dtype = "v2b" 
        #basedata: transaction info(vfilter/lfilter), vfilter: filter transaction from violas chain; \
        #        lfilter: filter transaction from violas chain. ex. basedata = "vfilter" 
        #load logging
        logger = log.logger.getLogger(name) 

        _vproof = vproof(name, ttype, dtype, stmanage.get_db(dtype), stmanage.get_db(basedata), stmanage.get_violas_nodes())
        _vproof.set_step(stmanage.get_db(dtype).get("step", 100))
        ret = _vproof.start()
        if ret.state != error.SUCCEED:
            logger.error(ret.message)

    except Exception as e:
        ret = parse_except(e)
    return ret
