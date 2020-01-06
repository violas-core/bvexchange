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
    _name = None
    _btc_chain = "btc"
    _violas_chain = "violas"
    def __init__(self, name = 'base', work = True):
        self._work = work
        self._name = name
        self._logger = getlogger(name) 

    def work(self):
        return self._work

    def work_stop(self):
        self._work = False

    def work_start(self):
        self._work = True

