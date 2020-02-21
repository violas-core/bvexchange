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

@app.route('/tranrecord/<string:sender>/<int:cursor>/<int:limit>/', methods=['GET'])
def get_transaction_record(sender, cursor = 0, limit = 99999999):
    try:
        module = None
        logger.debug(f"get record(sender={sender}, cursor={cursor}, limit={limit})")
        ret_violas = get_violas_record(sender, cursor, limit)
        if ret_violas.state != error.SUCCEED:
            raise "get transaction record failed.{chain = violas, sender = {sender}}"

        ret_libra = get_libra_record(sender, cursor, limit)
        if ret_libra.state != error.SUCCEED:
            raise "get transaction record failed.{chain = libra, sender = {sender}}"

        ret_btc = get_btc_record(sender, cursor, limit)
        if ret_btc.state != error.SUCCEED:
            raise "get transaction record failed.{chain = btc, sender = {sender}}"

        violas_datas = {}
        libra_datas = {}
        btc_datas = {}
        violas_datas.update(ret_violas.datas.get("datas"))
        libra_datas.update(ret_libra.datas.get("datas"))
        btc_datas.update(ret_btc.datas.get("datas"))
            
        datas = {"violas":[violas_datas[key] for key in sorted(violas_datas.keys())], \
                "libra":{(key, libra_datas[key]) for key in sorted(libra_datas.keys())}, \
                "btc":{(key, btc_datas[key]) for key in sorted(btc_datas.keys())} \
                }

        for key in list(datas.keys()):
            if len(datas[key]) == 0:
                del datas[key]

        ret =  result(error.SUCCEED, "", datas)

    except Exception as e:
        ret = parse_except(e)
    return ret.__repr__()

def get_proofdb(dtype):
    return stmanage.get_db(dtype)

def get_libra_record(sender, cursor, limit):
    try:
        flag = "LIBRA"
        rclient = requestclient("l2vrecord", get_proofdb("record"))
        ret = rclient.get_transaction_record(sender, flag, cursor = cursor, limit=limit)
        if ret.state != error.SUCCEED:
            raise f"get transaction record failed.chain = {flag}, sender = {sender}"

    except Exception as e:
        ret = parse_except(e)
    return ret

def get_violas_record(sender, cursor, limit):
    try:
        flag = "VIOLAS"
        rclient = requestclient("v2lrecord", get_proofdb("record"))
        ret = rclient.get_transaction_record(sender, flag, cursor = cursor, limit=limit)
        if ret.state != error.SUCCEED:
            raise f"get transaction record failed.chain = {flag}, sender = {sender}"

    except Exception as e:
        ret = parse_except(e)
    return ret

def get_btc_record(sender, cursor, limit):
    try:
        flag = "BTC"
        rclient = requestclient("b2vrecord", get_proofdb("record"))
        ret = rclient.get_transaction_record(sender, flag, cursor = cursor, limit=limit)
        if ret.state != error.SUCCEED:
            raise f"get transaction record failed.chain = {flag}, sender = {sender}"
    except Exception as e:
        ret = parse_except(e)
    return ret

