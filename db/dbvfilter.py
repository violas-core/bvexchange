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
from comm.error import error
from comm.result import result
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, UniqueConstraint, Index, String

from enum import Enum

#module name
name="dbv2b"

#load logging
logger = log.logger.getLogger(name) 

class dbvfilter:
    def __init__(self, host, port, db, passwd = None):
        pass
