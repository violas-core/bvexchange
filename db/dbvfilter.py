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
from comm.result import result
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, UniqueConstraint, Index, String

from enum import Enum

#module name
name="dbvfilter"

#load logging
logger = log.logger.getLogger(name) 

class dbvfilter:
    __key_latest_filter_ver = "latest_filter_ver"
    def __init__(self, host, port, db, passwd = None):
        self.__host = host
        self.__port = port
        self.__db = db
        self.__passwd = passwd
        self.__client = None
        ret = self.__connect(host, port, db, passwd)
        if ret.state != error.SUCCEED:
            raise Exception("connect db failed")

    def __connect(self, host, port, db, passwd = None):
        try:
            self.__client = redis.Redis(host=host, port=port, db=db, passwd=passwd)
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def set(self, key, value):
        try:
            self.__client.set(key, value)
            ret = result(error.SUCCEED)
        Exception as e:
            ret = parse_except(e)
        return ret

    def get(self, key):
        try:
            datas = self.__client.get(key)
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def key_is_exists(self, key):
        try:
            datas = self.__client.get(key)
            ret = result(error.SUCCEED, "", datas is None)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def delete(self, key):
        try:
            self,.__client.delete(key)
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def save(self):
        try:
            self.__client.save()
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def flush_db(self):
        try:
            self.__client.flushdb()
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def set_latest_filter_ver(self, ver):
        try:
            self.__client.set(self.__key_latest_filter_ver, ver)
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_latest_filter_ver(self):
        try:
            datas = self.__client.get(self.__key_latest_filter_ver)
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret
