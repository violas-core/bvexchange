#!/usr/bin/python3
'''
btc exchange vtoken db
'''
import operator
import sys,os,time,json
sys.path.append(os.getcwd())
sys.path.append("..")
import log
import log.logger
import traceback
import datetime
import sqlalchemy
import random
import redis
from comm.values import dbindexbase
from comm.error import error
from comm.result import result, parse_except
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, UniqueConstraint, Index, String

from baseobject import baseobject
from enum import Enum

#module name
name="dbvbase"

class dbvbase(baseobject):
    __key_latest_filter_ver     = "latest_filter_ver"
    __key_latest_saved_ver      = "latest_saved_ver"
    __key_min_valid_ver         = "min_valid_ver"

    dbindex = dbindexbase

    def __init__(self, name, host, port, db, passwd = None):
        baseobject.__init__(self, name)
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
            self._logger.debug(f"connect db(host={host}, port={port}, db={db}({self.db_name_to_value(db)}), passwd={password[:4]})")
            self._client = redis.Redis(host=host, port=port, db=self.db_name_to_value(db), password=password, decode_responses=True)
            self.set_mod_name(db)
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_mod_name(self):
        try:
            ret = self.get("mod_name")
        except Exception as e:
            ret = parse_except(e)
        return ret
            
    def select(self, name):
        try:
            self._client.select(self.db_name_to_value(name))
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def set_mod_name(self, name):
        try:
            ret = self.set("mod_name", name)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def db_name_to_value(self, name):
        for di in self.dbindex:
            if di.name == name.upper():
                return di.value
        raise ValueError(f"db name({name} unkown)")
    
    def pipeline(self):
        try:
            datas = self._client.pipeline(transaction = true)
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def pipeline(self):
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

    def scan(self, cursor, match = None, count = None):
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

    def hscan(self, name, cursor=0, match = None, count = None):
        try:
            pos, datas = self._client.hscan(name, cursor, match, count)
            ret = result(error.SUCCEED, "", (pos, datas))
        except Exception as e:
            ret = parse_except(e)
        return ret

    #**************sorted set********************************
    def zadd(self, name, mapping, nx=False, xx=False, ch=False, incr=False):
        try:
            datas = self._client.zadd(name, mapping, nx, xx, ch, incr)
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def zadd_one(self, name, key, value, nx=False, xx=False, ch=False, incr=False):
        try:
            datas = self._client.zadd(name, {value:key}, nx, xx, ch, incr)
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret
    def zcard(self, name):
        try:
            datas = self._client.zcard(name)
            ret = result(error.SUCCEED, "", int(datas))
        except exception as e:
            ret = parse_except(e)
        return ret

    def zcount(self, name, min, max):
        try:
            datas = self._client.zcount(name)
            ret = result(error.SUCCEED, "", int(datas))
        except exception as e:
            ret = parse_except(e)
        return ret

    def zincrby(self, name, value, amount):
        try:
            datas = self._client.zincrby(name, value, amount)
            ret = result(error.SUCCEED, "", datas)
        except exception as e:
            ret = parse_except(e)
        return ret

    def zrange(self, name, start, end, desc = False, withscores = False, score_cast_func=int):
        '''
            @start  : index , not score
            @end    : index , not score
            @desc   : desc spec, default 0 -> n
        '''
        try:
            datas = self._client.zrange(name, start, end, desc, withscores, score_cast_func)
            ret = result(error.SUCCEED, "", datas)
        except exception as e:
            ret = parse_except(e)
        return ret

    def zrank(self, name, value):
        try:
            datas = self._client.zrank(name, value)
            ret = result(error.SUCCEED, "", datas)
        except exception as e:
            ret = parse_except(e)
        return ret

    def zrem(self, name, values):
        try:
            datas = self._client.zrem(name, values)
            ret = result(error.SUCCEED, "", datas)
        except exception as e:
            ret = parse_except(e)
        return ret

    ##other remove api not support, use it ???

    def zscore(self, name, value):
        try:
            datas = self._client.zscore(name, value)
            ret = result(error.SUCCEED, "", datas)
        except exception as e:
            ret = parse_except(e)
        return ret

    def zscan(self, cursor = 0, match = None, count = None, \
            score_cast_func = int):
        try:
            datas = self._client.zscan(cursor = cursor, match = match, \
                    count = count, score_cast_func = score_cast_func)
            ret = result(error.SUCCEED, "", datas)
        except exception as e:
            ret = parse_except(e)
        return ret


    def zrevrange(self, name, start, end, withscores=False, \
                  score_cast_func=int):
        try:
            datas = self._client.zrevrange(name, start, end, withscores, score_cast_func)
            ret = result(error.SUCCEED, "", datas)
        except exception as e:
            ret = parse_except(e)
        return ret

    def zrevrangebyscore(self, name, max, min, start=None, num=None,
                         withscores=False, score_cast_func=int):
        try:
            datas = self._client.zrevrangebyscore(name, max, min, start, num, withscores, score_cast_func)
            ret = result(error.SUCCEED, "", datas)
        except exception as e:
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
            if datas is None or len(datas) == 0:
                datas = '-1'
            ret = result(error.SUCCEED, "", int(datas))
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
            if datas is None:
                datas = '-1'
            ret = result(error.SUCCEED, "", int(datas))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def list_version_keys(self, start = 0):
        keys = self.keys().datas
        return  sorted([int(key) for key in keys if key.isdigit() and int(key) >= start])

    def get_min_valid_ver(self):
        try:
            datas = self._client.get(self.__key_min_valid_ver)
            if datas is None:
                datas = '0'
            ret = result(error.SUCCEED, "", int(datas))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def set_min_valid_ver(self, ver):
        try:
            self._client.set(self.__key_min_valid_ver, ver)
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret


def test_new(client, name="client_test"):
    rname = name
    key1 = int(time.time() * 1000000)
    version = int(time.time() * 1000)
    address_chain = "00000000000000000000000000000000_BTC"
    #ret = client.zadd_one(rname, key1, json.dumps({"version":version, "address_chain":address_chain}))
    #assert ret.state == error.SUCCEED, f""

    #ret = client.hset(address_chain, version, json.dumps({"version":version, "timestamps": key1, "tran_id":address_chain}))
    #assert ret.state == error.SUCCEED, f""

    ret = client.zrevrangebyscore(name, max = 2596705822202818,  min = 1596707095497829, start = 0, num = 6, withscores = False)
    #ret = client.zrevrange(name, 14, -1)
    assert ret.state == error.SUCCEED, f""
    
    zvalues = ret.datas
    hkeys = []
    for  zvalue in zvalues:
        zvd = json.loads(zvalue)
        if not isinstance(zvd, dict):
            continue

        version = zvd.get("version")
        name = zvd.get("address_chain")
        ret = client.hget(name, version)
        assert ret.state == error.SUCCEED, f""
        print(ret.datas)

def test():
    client = dbvbase("test", "127.0.0.1", 6378, "test", "violas")
    test_new(client)
    

if __name__ == "__main__":
    test()
