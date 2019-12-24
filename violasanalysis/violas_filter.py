#!/usr/bin/python3
import operator
import sys, os
import json
sys.path.append(os.getcwd())
import log
import log.logger
import traceback
import datetime
import sqlalchemy
import setting
import requests
import comm
import comm.error
import comm.result
import comm.values
from comm.result import result, parse_except
from comm.error import error
from db.dbv2b import dbv2b
import violas.violasclient
from violas.violasclient import violasclient, violaswallet, violasserver
from enum import Enum

#module name
name="filter"

COINS = comm.values.COINS
#load logging
logger = log.logger.getLogger(name) 
    

