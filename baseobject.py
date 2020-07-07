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

    #@property
    #def from_chain(self):
    #    return self._from_chain

    #@from_chain.setter
    #def from_chain(self, name):
    #    self._from_chain = name

    #@property
    #def map_chain(self):
    #    return self._map_chain

    #@map_chain.setter
    #def map_chain(self, name):
    #    self._map_chain = name

    def check_state_raise(self, result, message):
        if result.state != error.SUCCEED:
            raise Exception(message)

    def append_property(self, name, value):
        setter(self, name, value)
