#!/usr/bin/python3
'''
btc exchange vtoken db
'''
import operator
import sys,os
sys.path.append(os.getcwd())
import log
import log.logger
import traceback
import datetime
import sqlalchemy
import setting
import random
import redis
import json
from comm.error import error
from comm.result import result, parse_except
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
logger = log.logger.getLogger(name) 

class dbvproof(dbvbase):
    def __init__(self, host, port, db, passwd = None):
        dbvbase.__init__(self. host, port, db, passwd)

    def __del__(self):
        dbvbase.__del__(self)

    def set_proof(self, key, value):
        try:
            dict = json.loads(value)
            tran_id = dict.get("tran_id", None)
            if tran_id is None or len(tran_id) <= 0:
                return result(error.ARG_INVALID)

            ret = self.set(key, value)
            if ret.state != error.SUCCEED:
                return ret

            ret = self.set(tran_id, key)

        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_proof_by_hash(self, hkey):
        try:
            ret = self.get(hkey)
            if ret.state != error.SUCCEED:
                reutrn ret

            return self.get(ret.datas)
        except Exception as e:
            ret = parse_except(e)
        return ret


    def get_proof_version(self, key):
        try:
            return self.get(key)
        except Exception as e:
            ret = parse_except(e)
        return ret
