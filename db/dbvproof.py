#!/usr/bin/python3
'''
btc exchange vtoken db
'''
import operator
import sys, os, time
sys.path.append(os.getcwd())
import traceback
import datetime
import sqlalchemy
import stmanage
import random
import redis
import json
from comm.error import error
from comm.result import result, parse_except
from comm.values import trantypebase
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, UniqueConstraint, Index, String
from db.dbvbase import dbvbase


from enum import Enum

#module name
name="dbvproof"

#load logging

class dbvproof(dbvbase):
    __KEY_MIN_VERSION_ = "min_version_"
    def __init__(self, name, host, port, db, passwd = None):
        dbvbase.__init__(self, name, host, port, db, passwd)
        self.__init_map_chain_name()

    def __init_map_chain_name(self):
        self._map_chain_name = {}
        for ttb in trantypebase:
            name = ttb.name.lower()
            self._map_chain_name.update({name[:1]:name})

    @property
    def map_chain_name(self):
        return self._map_chain_name

    def __del__(self):
        dbvbase.__del__(self)

    def set_proof(self, version, value):
        try:
            dict = json.loads(value)
            tran_id = dict.get("tran_id", None)
            if tran_id is None or len(tran_id) <= 0:
                return result(error.ARG_INVALID, "tran id is invalid.")

            ret = self.set(version, value)
            if ret.state != error.SUCCEED:
                return ret

            ret = self.set(tran_id, version)

        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_proof_by_hash(self, tran_id):
        try:
            ret = self.get(tran_id)
            if ret.state != error.SUCCEED:
                return ret

            version = ret.datas
            if version is None or len(version) == 0:
                return result(error.TRAN_INFO_INVALID, f"not found proof, tran_id: {tran_id}.")
            
            return self.get(ret.datas)
        except Exception as e:
            ret = parse_except(e)
        return ret


    def get_proof_version(self, version):
        try:
            return self.get(version)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def set_proof_min_version_for_state(self, version, state):
        try:
            ret = self.set(f"{self.__KEY_MIN_VERSION_}{state.lower()}", version)
        except Exception as e:
            ret = parse_except(e)
        return ret
    def set_proof_min_version_for_start(self, version):
        return self.set_proof_min_version_for_state(version, "start")

    def set_proof_min_version_for_cancel(self, version):
        return self.set_proof_min_version_for_state(version, "cancel")

    def set_proof_min_version_for_stop(self, version):
        return self.set_proof_min_version_for_stop(version, "stop")

    def get_proof_min_version_for_state(self, state):
        try:
            ret = self.get(f"{self.__KEY_MIN_VERSION_}{state.lower()}")
            if ret.state == error.SUCCEED:
                if ret.datas is None:
                    ret = result(error.SUCCEED, "", '0')
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_proof_min_version_for_start(self):
        return get_proof_min_version_for_state(state, "start")

    def get_proof_min_version_for_cancel(self):
        return get_proof_min_version_for_state(state, "cancel")

    def get_proof_min_version_for_stop(self):
        return get_proof_min_version_for_state(state, "stop")

    def create_haddress_name(self, tran_info):
        return f"{tran_info['sender']}_{tran_info['flag']}"

    def create_haddress_key(self, tran_info):
        return f"{tran_info['version']}"


    def get_chain_name(self, dtype):
        from_chain = "violas"
        to_chain = "violas"


        if dtype is None:
            return (form_chain, to_chain)
        if dtype[0] == "v":
            from_chain = "violas"
            

    def create_haddress_value(self, tran_info):
        dtype = tran_info.get("type", "v2v")
        return json.dumps({"version":tran_info["version"], \
            "type":tran_info["type"], \
            "opttype":tran_info["opttype"], \
            "expiration_time":int(tran_info.get("expiration_time")),\
            "state":tran_info["state"], \
            "to_address":tran_info["to_address"], \
            "tran_id":tran_info["tran_id"], \
            "in_amount":tran_info["amount"], \
            "out_amount": int(tran_info["out_amount_real"]), \
            "in_token" : tran_info.get("token_id"), \
            "out_token": stmanage.get_type_stable_token(tran_info["type"]), \
            "timestamps": int(time.time() * 1000000), \
            "from_chain": self.map_chain_name[dtype[:1]], \
            "to_chain": self.map_chain_name[dtype[2:3]], \
            "times" : tran_info.get("times", 0), \
            })
