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
from comm.result import result, parse_except
from comm.error import error
from enum import Enum
getlogger = log.logger.getLogger
class baseobject(object):
    def __init__(self, name = 'base', work = True):
        self._name = None
        self._logger = None
        self._from_chain = None
        self._map_chain = None
        self._work = work
        self._name = name

        if self._logger is None:
            self._logger = getlogger(name) 

    def work(self):
        return self._work

    def work_stop(self):
        self._work = False

    def work_start(self):
        self._work = True

    def name(self):
        return self._name

    def init_defalut_property(self):
        ppts = {"from_chain": None, "map_chain":None, }
        for name, value in ppts.items:
            self.append_property(name, value)

    def check_state_raise(self, result, message):
        if result.state != error.SUCCEED:
            raise Exception(message)

    def append_property(self, name, value, new = True):
        if new:
            setattr(self, name.strip(), value)

    def get_property(self, name):
        ret getattr(self, name.strip())

    def create_senders_key(self, chain):
        return f"{chain}_senders"

    def create_wallet_key(self, chain):
        return f"{chain}_wallet"

    def create_client_key(self, chain):
        return f"{chain}_client"

    def create_nodes_key(self, chain):
        return f"{chain}_nodes"
