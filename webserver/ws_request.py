#!/usr/bin/python3
from flask import Flask
app = Flask(__name__)

import operator
import sys, os
import json
sys.path.append(os.getcwd())
sys.path.append("..")
import log
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
from db.dbv2b import dbv2b
from btc.btcclient import btcclient
import vlsopt.violasclient
from vlsopt.violasclient import violasclient, violaswallet, violasserver
from vlsopt.violasproof import violasproof
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from baseobject import baseobject
from enum import Enum
from vrequest.request_client import requestclient

#module self.name
mod_name="webserver"
logger = log.logger.getLogger(mod_name)

@app.route('/')
def test():
    return "hello world."

@app.route('/tranrecord/<string:dtype>/<string:sender>/<string:module>/<int:cursor>/<int:limit>', methods=['GET', 'POST'])
def get_transaction_record(dtype, sender, module, cursor = 0, limit = 10):
    try:
        logger.debug(f"get {dtype} record(sender={sender}, module={module}, cursor={cursor}, limit={limit})")
        if dtype == "v2l":
            ret = get_v2l_record(sender, module, cursor, limit)
        elif dtype == "l2v":
            ret = get_l2v_record(sender, module, cursor, limit)
        elif dtype == "v2b":
            ret = get_v2b_record(sender, module, cursor, limit)
        elif dtype == "b2v":
            ret = get_b2v_record(sender, module, cursor, limit)
        else:
            ret = result(error.ARG_INVALID, f"dtype = {dytpe} not found.")
    except Exception as e:
        ret = parse_except(e)
    return ret.__repr__()

def get_proofdb(dtype):
    return stmanage.get_db(dtype)

def get_l2v_record(sender, module, cursor, limit):
    try:
        rclient = requestclient("l2vrecord", get_proofdb("l2v"))
        ret = rclient.get_transaction_record(sender, module, cursor = cursor, limit=limit)
    except Exception as e:
        ret = parse_except(e)
    return ret

def get_v2l_record(sender, module, cursor, limit):
    try:
        rclient = requestclient("v2lrecord", get_proofdb("v2l"))
        ret = rclient.get_transaction_record(sender, module, cursor = cursor, limit=limit)
    except Exception as e:
        ret = parse_except(e)
    return ret

def get_v2b_record(sender, module, cursor, limit):
    try:
        rclient = requestclient("v2brecord", get_proofdb("v2b"))
        ret = rclient.get_transaction_record(sender, module, cursor = cursor, limit=limit)
    except Exception as e:
        ret = parse_except(e)
    return ret

def get_b2v_record(sender, module, cursor, limit):
    try:
        rclient = requestclient("b2vrecord", get_proofdb("b2v"))
        ret = rclient.get_transaction_record(sender, module, cursor = cursor, limit=limit)
    except Exception as e:
        ret = parse_except(e)
    return ret

