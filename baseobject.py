#!/usr/bin/python3
import operator
import sys, os
import json
import log
sys.path.append(os.getcwd())
import log.logger
import traceback
import datetime
import sqlalchemy
import stmanage
import requests
import comm
import comm.error
import comm.result
import comm.values
from multiprocessing import Lock
from comm.result import result, parse_except
from comm.error import error
from enum import Enum
from comm.values import (
        trantypebase as trantype,
        datatypebase as datatype
        )

getlogger = log.logger.getLogger
exe_lock = Lock()
class baseobject(object):
    def __init__(self, name = 'base', work = True, chain = None):
        self._name = None
        self._logger = None
        self._from_chain = None
        self._map_chain = None
        self.__chain = chain
        self._work = work
        self._name = name
        self.append_property("usd_exe_lock", False)

        if self._logger is None:
            self._logger = getlogger(name) 

    @property
    def chain(self):
        return self.__chain

    def work(self):
        return self._work

    def work_stop(self):
        self._work = False

    def work_start(self):
        self._work = True

    def open_lock(self, value = False):
        self.usd_exe_lock = value

    def close_lock(self):
        self.usd_exe_lock = False

    def lock(self):
        try:
            if self.usd_exe_lock:
                exe_lock.acquire()
        except Exception as e:
            pass


    def unlock(self):
        try:
            if self.usd_exe_lock:
                exe_lock.release()
        except Exception as e:
            pass

    def name(self):
        return self._name

    def init_defalut_property(self):
        ppts = {"from_chain": None, "map_chain":None, }
        for name, value in ppts.items:
            self.append_property(name, value)

    def check_state_raise(self, result, message):
        if result.state != error.SUCCEED:
            raise Exception(f"{message} error: {result.message}")

    def append_property(self, name, value, new = True):
        if new:
            setattr(self, name.strip(), value)

    def get_property(self, name):
        return getattr(self, name.strip())

    @classmethod
    def to_str(self, data):
        if not data:
            return data

        if isinstance(data, str):
            return data
        return data.value
         
    def create_senders_key(self, chain):
        return f"{self.to_str(chain)}_senders"

    def create_wallet_key(self, chain):
        return f"{self.to_str(chain)}_wallet"

    def create_client_key(self, chain):
        return f"{self.to_str(chain)}_client"

    def create_nodes_key(self, chain):
        return f"{self.to_str(chain)}_nodes"

    def create_point_key(self, key, prefix = None):
        key = f"{prefix}_{key}" if prefix else key
        return key

    def is_need_mint_mtoken(self, dtype):
        if not isinstance(dtype, str):
            dtype = dtype.value

        if dtype and len(dtype) > 3:
            return dtype[1:4] == "2vm" and len(dtype) == 4

        return False


    def is_need_burn_mtoken(self, dtype):
        if not isinstance(dtype, str):
            dtype = dtype.value

        if dtype and len(dtype) > 3:
            return dtype[0:2] == "v2" and dtype[3] == "m" and len(dtype) == 4

        return False

    def get_address_from_account(self, account):
        if not isinstance(account, str):
            address = account.address
            if not isinstance(address, str):
                address = address.hex()
        else:
            address = account
        return address

    def get_combine_address(self, combine_account, receiver):
        if combine_account:
            return self.get_address_from_account(combine_account)

        if receiver:
            return self.get_address_from_account(receiver)
        return None

    #check local db module
    def use_module(self, state, module_state):
        return state is None or state.value < module_state.value

