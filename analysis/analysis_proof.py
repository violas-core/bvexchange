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
from analysis.analysis_base import abase

#module name
name="aproof"

COINS = comm.values.COINS
class aproof(abase):
    class proofstate(Enum):
        START   = 1
        END     = 2
        CANCEL  = 3
        STOP    = 4
        UNKOWN = 255

    def __init__(self, name = "vproof", 
            ttype = "violas",       #metadata  flag: chain name(violas/libra)
            dtype = "v2lusd",       #metadata  type:v2lxxx/l2vxxx
            dbconf = None,          #save analysis result db conf
            fdbconf = None,         #base data from lfilter/vfilter db conf
            rdbconf = None,         #save transaction record db conf 
            nodes = None,           #chain nodes libra/violas
            chain = "violas"):
        self._fdbclient = None
        #db use dbvproof, dbvfilter, not use violas/libra nodes
        super().__init__(name, ttype, dtype, None, nodes, chain)
        self._dbclient = None
        self._fdbclient = None
        if dbconf is not None:
            self._dbclient = dbvproof(name, dbconf.get("host"), dbconf.get("port"), \
                    dbconf.get("db"), dbconf.get("password"))
        if fdbconf is not None:
            self._fdbclient = dbvfilter(name, fdbconf.get("host"), fdbconf.get("port"), \
                    fdbconf.get("db"), fdbconf.get("password"))

        self.init_valid_state()

    def __del__(self):
        super().__del__()
        if self._fdbclient is not None:
            self._fdbclient.save()

    def stop(self):
        super().stop()

    def init_valid_state(self):
        setattr(self, "valid_state", \
                [state.name.lower() for state in self.proofstate if state != self.proofstate.UNKOWN])

        
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

    def is_valid_datatype(self, dtype):
        return dtype in self.get_data_types()

    def check_tran_is_valid(self, tran_info):

        if tran_info.get("flag", None) not in self.get_tran_types():
            self._logger.warning(f"flag({tran_info.get('flag', None)}) is invalid.")
            return False

        if self.proofstate_name_to_value(tran_info.get("state", None)) == self.proofstate.UNKOWN:
            self._logger.warning(f"state({tran_info.get('state', None)}) is invalid.")
            return False

        if not self.is_valid_datatype(tran_info.get("type")):
            self._logger.warning(f"type({tran_info.get('type', None)}) is invalid.")
            return False

        if not self.is_valid_token_id(tran_info.get("token_id")): 
            self._logger.warning(f"token_id({tran_info.get('token_id', None)}) is invalid.token_id:{self._token_id}")
            return False

        return True

        #return tran_info.get("flag", None) in self.get_tran_types() and \
        #       self.proofstate_name_to_value(tran_info.get("state", None)) != self.proofstate.UNKOWN and \
        #       self.is_valid_datatype(tran_info.get("type")) and \
        #       self.is_valid_token_id(tran_info.get("token_id")) 

    def is_valid_proofstate_change(self, new_state, old_state):
        if new_state == self.proofstate.START:
            return True

        if new_state in (self.proofstate.END, self.proofstate.CANCEL, self.proofstate.STOP) and old_state == self.proofstate.START:
            return True

        if new_state in [self.proofstate.STOP] and old_state == self.proofstate.CANCEL:
            return True

        return False

    def get_tran_id(self, tran_info):
        if tran_info["flag"] == self.trantype.BTC:
            tran_id = tran_info["tran_id"]
        else:
            tran_id = self.create_tran_id(tran_info["flag"], tran_info["type"], tran_info['sender'], \
                    tran_info['receiver'], tran_info['module'], tran_info['version'])
        return tran_id

    def is_btc_data(self, tran_info):
        return tran_info["flag"] == self.trantype.BTC

    def update_proof_info_for_btc(self, version, train_id, tran_info):
        tran_info["flag"] = tran_info["flag"].value
        tran_info["type"] = tran_info["type"].value
        tran_id = tran_info["tran_id"]
        ret = self._dbclient.set_proof(version, json.dumps(tran_info))
        if ret.state != error.SUCCEED:
            return ret
        return result(error.SUCCEED, "", {"new_proof":True, "tran_id":tran_id})

    def has_update_state_authority(self, state, old_tran_info, new_tran_info):
        #only recevier can change state (start -> end/cancel)

        old_sender = old_tran_info["sender"]
        old_receiver = old_tran_info["receiver"]
        new_sender = new_tran_info["sender"]
        new_receiver = new_tran_info["receiver"]

        if state in (self.proofstate.END, self.proofstate.STOP):
            return old_receiver == new_sender
        elif state == self.proofstate.CANCEL:
            return old_sender == new_sender

        return False

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

                #found key = version info, db has old datas , must be flush db?
                if ret.datas == True:
                    return result(error.TRAN_INFO_INVALID, f"key{version} is exists, db datas is old, flushdb ?. violas tran info : {tran_info}")

                #create tran id
                tran_id = self.get_tran_id(tran_info)

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
                    #btc transaction is end , 
                    #diff libra and violas(maybe state is changed to end before scan bitcoin chain. so proof db can't found.)
                    if self.is_btc_data(tran_info):
                        return self.update_proof_info_for_btc(version, tran_id, tran_info)

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

    def update_min_version_for_state(self, state):
        try:
            self._logger.debug(f"start update_min_version_for_state")
            #update min version for state is start
            ret = self._dbclient.get_proof_min_version_for_state(state)
            if ret.state != error.SUCCEED:
                return ret
            start_version = max(int(ret.datas), self.get_min_valid_version())

            ret = self._dbclient.get_latest_saved_ver()
            if ret.state != error.SUCCEED:
                return ret
            max_version = ret.datas

            keys = self._dbclient.list_version_keys(start_version)
            new_version = start_version
            for version in keys:
                if self.work() != True:
                    break
                    
                #self._logger.debug(f"check version {version}")

                ret = self._dbclient.get(version)
                if ret.state != error.SUCCEED:
                    return ret

                if ret.datas is None:
                    continue

                new_version = version
                tran_data = json.loads(ret.datas)
                if tran_data.get("state") in self.valid_state and \
                        self.is_valid_token_id(tran_data.get("token_id")):
                    break

            ret = self._dbclient.set_proof_min_version_for_state(new_version, state)
            if ret.state == error.SUCCEED and start_version != new_version:
                self._logger.info(f"update min version for {state}(proof state) {start_version} -> {version}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def start(self):
        try:
            self._logger.debug(f"start proof work")

            new_state = "start"
            ret = self._dbclient.get_latest_filter_ver()
            if ret.state != error.SUCCEED:
                return ret

            start_version = self.get_start_version(ret.datas + 1)

            #can get max version 
            ret = self._fdbclient.get_latest_saved_ver()
            if ret.state != error.SUCCEED:
                return ret
            latest_saved_ver = ret.datas
            max_version = latest_saved_ver

            #not found new transaction to change state
            if start_version > max_version:
                self._logger.debug(f"dtype:{self.name()} not found new transaction. " + 
                        f"start version:{start_version} " + 
                        f"max saved version:{max_version} :chain : {self.from_chain}")
                return result(error.SUCCEED)

            version  = start_version
            count = 0
            self._logger.debug(f"proof({self.name()}) start version = {start_version} " +
                f"step = {self.get_step()} valid transaction latest_saved_ver = {latest_saved_ver} ")

            keys = self._fdbclient.list_version_keys(start_version)
            latest_filter_ver = start_version
            for version in keys:
                try:
                    if count >= self.get_step() and self.work() == False:
                        break
                    #record last version(parse), maybe version is not exists
                    self._logger.debug(f"parse transaction:{version}")

                    latest_filter_ver = version

                    ret = self._fdbclient.get(version)
                    if ret.state != error.SUCCEED:
                        return ret

                    if ret.datas is None:
                        continue

                    tran_data = json.loads(ret.datas)
                    ret = self.parse_tran(tran_data)
                    if ret.state != error.SUCCEED: 
                        continue

                    tran_filter = ret.datas
                    if self.check_tran_is_valid(tran_filter) != True:
                        continue

                    self._logger.debug(f"transaction parse: {tran_filter}")

                    #this is target transaction, todo work here
                    ret = self.update_proof_info(tran_filter)
                    if ret.state != error.SUCCEED:
                        self._logger.error(ret.message)
                        continue
                    update_ret = ret.datas

                    #mark it, watch only, True: new False: update
                    # maybe btc not save when state == end, because start - > end some minue time
                    if update_ret.get("new_proof") == True:  
                        self._dbclient.set_latest_saved_ver(version)

                    tran_id = update_ret.get("tran_id")
                    ret = self._dbclient.get_proof_by_hash(tran_id)
                    if ret.state != error.SUCCEED:
                        return ret
                    
                    if (ret.datas is not None or len(ret.datas) > 0) and self.can_record():
                        ret = self._rdbclient.update_address_info(json.loads(ret.datas))
                        if ret.state != error.SUCCEED:
                            return ret
                    count += 1
                except Exception as e:
                    ret = parse_except(e)
                finally:
                    #version += 1
                    pass

            #here version is not analysis
            self._dbclient.set_latest_filter_ver(latest_filter_ver)
            for state in ["start", "stop", "cancel"]:
                self.update_min_version_for_state(state)
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        finally:
            self._logger.debug("end vproof work")

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
