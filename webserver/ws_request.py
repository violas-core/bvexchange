#!/usr/bin/python3
from flask import Flask , url_for, request
from markupsafe import escape
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
import tools.show_workenv

#module self.name
mod_name="webserver"
logger = log.logger.getLogger(mod_name)

@app.route('/')
def main():
    args    = request.args
    opt     = args.get("opt")
    chain   = args.get("chain")
    cursor  = int(args.get("cursor", 0))
    limit   = int(args.get("limit", 10))
    dtype   = args.get("dtype")
    sender  = args.get("sender")
    version = args.get("version")

    if opt is None:
        raise Exception("opt not found.")
    if opt == "address":
        return tranaddress(chain, cursor, limit)
    elif opt == "record":
        return tranrecord(chain, sender, cursor, limit)
    elif opt == "detail":
        return trandetail(dtype, version)
    elif opt == "workstate":
        return workstate()
    else:
        raise Exception("opt not found.")


@app.route('/trandetail/<string:dtype>/<string:version>/', methods=['GET'])
def trandetail(dtype, version):
    try:
        logger.debug(f"get record detail(dtype = {dtype}, version={version})")
        rclient = requestclient(f"{dtype}record", get_proofdb(dtype))

        ret = rclient.get_tran(version)
        if ret.state != error.SUCCEED:
            raise f"get transaction record detail failed dtype = {dtype}, version={version}"
        datas = {"dtype": dtype,\
                "version": version, \
                "datas": ret.datas}
        ret = result(error.SUCCEED, "", datas)
    except Exception as e:
        ret = parse_except(e)
    return ret.to_json()

@app.route('/tranaddress/<string:chain>/<int:cursor>/<int:limit>/', methods=['GET'])
def tranaddress(chain, cursor = 0, limit = 99999999):
    try:
        logger.debug(f"get record address(chain = {chain}, cursor={cursor}, limit={limit})")

        check_chain(chain)

        rclient = requestclient("l2vrecord", get_proofdb("record"))
        ret = rclient.list_record_address_for_chain(chain, cursor = cursor, limit=limit)
        if ret.state != error.SUCCEED:
            raise f"get transaction record failed chain = {chain}"
        datas = {"cursor": ret.datas[0],\
                "count": len(ret.datas[1]), \
                "datas": [data[:0 - len(chain) -1] for data in ret.datas[1]]}
        ret = result(error.SUCCEED, "", datas)
    except Exception as e:
        ret = parse_except(e)
    return ret.to_json()

@app.route('/tranrecord/<string:chain>/<string:sender>/<int:cursor>/<int:limit>/', methods=['GET'])
def tranrecord(chain, sender, cursor = 0, limit = 99999999):
    try:
        logger.debug(f"get record(chain = {chain} sender={sender}, cursor={cursor}, limit={limit})")

        check_chain(chain)

        rclient = requestclient("l2vrecord", get_proofdb("record"))
        ret = rclient.get_transaction_record(sender, chain, cursor = cursor, limit=limit)
        if ret.state != error.SUCCEED:
            raise f"get transaction record failed.chain = {chain}, sender = {sender}, cursor={cursor}, limit={limit}"
        datas = {"cursor": ret.datas[0],\
                "count": len(ret.datas[1]), \
                "datas":[json.loads(ret.datas[1][key]) for key in sorted(ret.datas[1].keys())] \
                }
        ret = result(error.SUCCEED, "", datas)
    except Exception as e:
        ret = parse_except(e)
    return ret.to_json()

def check_chain(chain):
    if chain is None or chain.upper() not in ("VIOLAS", "LIBRA", "BTC"):
        raise Exception(f"{chain} is invalid. must be [VIOLAS, LIBRA, BTC]")

def get_chain_record(flag, sender, cursor, limit):
    try:
        flag = "LIBRA"
        rclient = requestclient("l2vrecord", get_proofdb("record"))
        ret = rclient.get_transaction_record(sender, flag, cursor = cursor, limit=limit)
        if ret.state != error.SUCCEED:
            raise Exception(f"get transaction record failed.chain = {flag}, sender = {sender}")

    except Exception as e:
        ret = parse_except(e)
    return ret
def get_proofdb(dtype):
    return stmanage.get_db(dtype)

@app.route('/workstate/', methods=['GET'])
def workstate():
    return tools.show_workenv.show_all()

'''
with app.test_request_context():
    logger.debug(url_for('tranaddress', chain = "violas", cursor = 0, limit = 10))
    logger.debug(url_for('tranrecord', chain = "violas", sender="af5bd475aafb3e4fe82cf0d6fcb0239b3fe11cef5f9a650e830c2a2b89c8798f", cursor=0, limit=10))
    logger.debug(url_for('trandetail', dtype="v2b", version="5075154"))
'''

if __name__ == "__main__":
    from werkzeug.contrib.fixers import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.run()
