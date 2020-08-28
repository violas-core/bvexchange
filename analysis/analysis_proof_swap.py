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
class aproofswap(aproofbase):

    def __init__(self, name = "vproof", 
            ttype = "violas",       #ttype violas/libra
            dtype = "swap",         #metadata  type:swap
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
        tran_id = self.create_tran_id(tran_info["flag"], tran_info["type"], tran_info['sender'], \
                tran_info['receiver'], tran_info['module'], tran_info['version'])
        return tran_id

    def update_proof_info(self, tran_info):
        try:
            self._logger.debug(f"start update_proof_info tran info: {tran_info}")
            version = tran_info.get("version", None)

            tran_id = None

            self._logger.debug(f"new proof: {new_proof}")
            ret = result(error.SUCCEED, "", {"new_proof":True, "tran_id":tran_id, "state": tran_info["state"]})
        except Exception as e:
            ret = parse_except(e)
        return ret

