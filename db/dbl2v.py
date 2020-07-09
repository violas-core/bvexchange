#!/usr/bin/python3
'''
vlibra libra exchange vtoken db
'''
import operator
import sys,os
sys.path.append(os.getcwd())
sys.path.append("..")
import log
import log.logger
import traceback
import datetime
import sqlalchemy
import stmanage
import random
import comm
from comm.error import error
from comm.result import result
from comm.result import parse_except
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, UniqueConstraint, Index, String

from baseobject import baseobject
from enum import Enum
from db.dbv2l import dbv2l

#module name
name="dbl2v"

class dbl2v(dbv2l):
    def __init__(self, name, dbfile):
        dbv2l.__init__(self, name, dbfile)

