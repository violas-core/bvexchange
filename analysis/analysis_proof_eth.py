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
name="aproofswap"
class aproofeth(aproofbase):

    def __init__(self, name = "vproof", 
            ttype = "ethereum",       #ttype ethereum
            dtype = "e2vm",         #metadata  type:e2vm
            dbconf = None,          #save analysis result db conf
            fdbconf = None,         #base data from efilter db conf
            rdbconf = None,         #save transaction record db conf 
            nodes = None,            #chain nodes ethereum
            chain = "ethereum"
            ):
        super().__init__(name, ttype, dtype, dbconf, fdbconf, rdbconf, nodes, chain)

    def __del__(self):
        super().__del__()

    def stop(self):
        super().stop()

    def get_tran_id(self, tran_info):
        tran_id = tran_info["sender"] + "_" + tran_info["sequence"]
        return tran_id

    def update_proof_info(self, tran_info):
        try:
            self._logger.debug(f"start update_proof_info tran info: {tran_info}")
            version = tran_info.get("version", None)

            #create tran id
            tran_id = self.get_tran_id(tran_info)
            new_proofstate = self.proofstate_name_to_value(tran_info.get("state", ""))

            #state is not start
            ret  = self._dbclient.key_is_exists(tran_id)
            if ret.state != error.SUCCEED:
                return ret
            found = ret.datas

            new_proof = (new_proofstate == self.proofstate.START) or not found)

            self._logger.debug(f"new proof: {new_proof}")
            if new_proof:
                tran_info["flag"] = tran_info["flag"].value
                tran_info["type"] = tran_info["type"].value
                tran_info["tran_id"] = tran_id

                ret = self._dbclient.set_proof(version, json.dumps(tran_info))
                if ret.state != error.SUCCEED:
                    return ret
                self._logger.info(f"saved new proof succeed. version = {tran_info.get('version')} tran_id = {tran_id} state={tran_info['state']}")

            else:
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

                db_tran_info["state"] = tran_info["state"]
                self._dbclient.set_proof(db_tran_info.get("version"), json.dumps(db_tran_info))
                self._logger.info(f"change state succeed. version = {db_tran_info.get('version')} tran_id = {db_tran_id} state={db_tran_info['state']}")

            ret = result(error.SUCCEED, "", {"new_proof":new_proof, "tran_id":tran_id, "state": tran_info["state"]})
        except Exception as e:
            ret = parse_except(e)
        return ret

