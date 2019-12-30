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
from comm.error import error
from comm.result import result, parse_except
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, UniqueConstraint, Index, String

from enum import Enum

#module name
name="dbvbase"

#load logging
logger = log.logger.getLogger(name) 

class dbvbase(object):
    __key_latest_filter_ver = "latest_filter_ver"
    __key_latest_saved_ver = "latest_saved_ver"
    def __init__(self, host, port, db, passwd = None):
        self.__host = host
        self.__port = port
        self.__db = db
        self.__passwd = passwd
        self._client = None
        ret = self.__connect(host, port, db, passwd)
        if ret.state != error.SUCCEED:
            raise Exception("connect db failed")

    def __del__(self):
        self._client.save() 
        self._client.close() 

    def __connect(self, host, port, db, password = None):
        try:
            logger.debug(f"connect filter db(host={host}, port={port}, db={db}, passwd={password})")
            self._client = redis.Redis(host=host, port=port, db=db, password=password, decode_responses=True)
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def pipeline():
        try:
            datas = self._client.pipeline(transaction = true)
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def pipeline():
        try:
            self._client.execute()
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def set(self, key, value):
        try:
            self._client.set(key, value)
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def mset(self, *args, **kwargs):
        try:
            self._client.mset(args, kwargs)
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get(self, key):
        try:
            datas = self._client.get(key)
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def key_is_exists(self, key):
        try:
            datas = self._client.exists(key)
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def delete(self, key):
        try:
            self._client.delete(key)
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def keys(self):
        try:
            datas = self._client.keys()
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def type(self, key):
        try:
            datas = self._client.type(key)
            ret = result(error.SUCCEED, "", typte)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def scan(cursor, match = None, count = None):
        try:
            pos, datas = self._client.scan(cursor, match, count)
            ret = result(error.SUCCEED, "", (pos, datas))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def hset(self, name, key, value):
        try:
            self._client.hset(name, key, value)
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def hget(self, name, key):
        try:
            datas = self._client.hget(name, key)
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def hgetall(self, name):
        try:
            datas = self._client.hgetall(name)
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def hlen(self, name):
        try:
            datas = self._client.hlen(name)
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def hkeys(self, name):
        try:
            datas = self._client.hkeys(name)
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def hvals(self, name):
        try:
            datas = self._client.hvals(name)
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def hexists(self, name, key):
        try:
            datas = self._client.hexists(name, key)
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def hdel(self, name, key):
        try:
            datas = self._client.hdel(name, key)
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def hscan(name, cursor, match = None, count = None):
        try:
            pos, datas = self._client.hscan(name, cursor, match, count)
            ret = result(error.SUCCEED, "", (pos, datas))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def save(self):
        try:
            self._client.save()
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def flush_db(self):
        try:
            self._client.flushdb()
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def set_latest_filter_ver(self, ver):
        try:
            self._client.set(self.__key_latest_filter_ver, ver)
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_latest_filter_ver(self):
        try:
            datas = self._client.get(self.__key_latest_filter_ver)
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def set_latest_saved_ver(self, ver):
        try:
            self._client.set(self.__key_latest_saved_ver, ver)
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_latest_saved_ver(self):
        try:
            datas = self._client.get(self.__key_latest_saved_ver)
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret
