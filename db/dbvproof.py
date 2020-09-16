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

    @classmethod
    def map_opttype(self, opttype):
        if opttype in ("v2vswap"):
            return "swap"
        elif opttype in ("fpswap"): #fund proof swap
            return "fpswap"
        return opttype

    def create_haddress_name(self, tran_info):
        opttype = self.map_opttype(tran_info['opttype'])
        return f"{tran_info['sender']}_{tran_info['flag']}_{opttype}"

    def create_haddress_key(self, tran_info):
        return f"{tran_info['version']}"


    def get_chain_name(self, dtype):
        from_chain = "violas"
        to_chain = "violas"

        if dtype is None:
            return (form_chain, to_chain)
        if dtype[0] == "v":
            from_chain = "violas"
            

    def get_out_token(self, tran_info):
        opttype = tran_info["opttype"]
        out_token = ""
        if opttype == "map":
            out_token = stmanage.get_token_map(tran_info["token_id"])
        elif opttype in ("v2vswap", "fpswap"):
            out_token = tran_info.get("out_token")
        else : #swap for diff chain
            out_token = stmanage.get_type_stable_token(tran_info["type"])
        return out_token

    def map_state(self, state):
        if state == "prestart":
            state = "start"
        return state

    def create_haddress_value(self, tran_info):
        dtype = tran_info.get("type", "v2v")
        timestamps = tran_info.get("timestamps", int(time.time() * 1000000))
        exp_time = int(tran_info.get("expiration_time")) * 1000000
        if timestamps > exp_time:
            timestamps = exp_time
        return {"version":tran_info["version"], \
            "type":tran_info["type"], \
            "opttype":tran_info["opttype"], \
            "expiration_time":int(timestamps/1000000),\
            "state":self.map_state(tran_info["state"]), \
            "to_address":tran_info["to_address"], \
            "tran_id":tran_info["tran_id"], \
            "in_amount":tran_info["amount"], \
            "out_amount": int(tran_info["out_amount_real"]), \
            "in_token" : tran_info.get("token_id"), \
            "out_token": self.get_out_token(tran_info), \
            "timestamps": timestamps, \
            "from_chain": self.map_chain_name[dtype[:1]], \
            "to_chain": self.map_chain_name[dtype[2:3]], \
            "times" : tran_info.get("times", 0), \
            }

    def record_index_name(self, opttype):
        opttype = self.map_opttype(opttype)
        return f"{opttype}_record_index"

    def create_zset_value(self, name, key, tran_info = None):
        return json.dumps({"name":name, "key":key})

        pass
    def set_record(self, name, key, timestamps, tran_info):
        '''save record to record db
           @name: hhash name: address_<chain:btc/violas/libra>_<opttype:map/swap>
           @key : hhash key: version
           @tran_info: hhash value: should to dumps, here is dict type
        '''
        zname = self.record_index_name(tran_info["opttype"])
        zkey = timestamps
        zvalue = self.create_zset_value(name, key, tran_info)
        #check

        ret = self.zadd_one(zname, zkey, zvalue)
        if ret.state != error.SUCCEED:
            return ret

        ret = self.hset(name, key, json.dumps(tran_info))
        return ret

    def update_record(self, name, key, tran_info):
        ret = self.hset(name, key, json.dumps(tran_info))
        return ret

    def get_record(self, name, key):
        ret = self.hget(name, key)
        return ret

    def get_records(self, opttype, names, start = 0, limit = 10):
        '''save record to record db
           @opttype: record type. swap or map
           @name: hhash name: address_<chain:btc/violas/libra>_<opttype:map/swap>
        '''
        zname = self.record_index_name(opttype)
        ret = self.zrevrange(zname, 0, -1)
        if ret.state != error.SUCCEED:
            return ret
        datas = []
        index = -1
        zvals = ret.datas
        for zval in zvals:
            dict_zval = json.loads(zval)
            hname = dict_zval.get("name")
            key = dict_zval.get("key")
            if hname in names:
                index = index + 1

            if index >= start:
                ret = self.hget(hname, key)
                if ret.state != error.SUCCEED:
                    return ret
                
                datas.append(ret.datas)

            if len(datas) >= limit and limit > 0:
                break

        ret = result(error.SUCCEED, datas = datas)
        return ret

