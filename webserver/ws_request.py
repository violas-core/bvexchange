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
    try:
        stmanage.set_conf_env_default()
        args    = request.args
        opt     = args.get("opt")
        chain   = args.get("chain")
        cursor  = int(args.get("cursor", 0))
        limit   = int(args.get("limit", 10))
        dtype   = args.get("dtype")
        sender  = args.get("sender")
        senders  = args.get("senders")
        version = args.get("version")
        opttype = args.get("opttype", "swap")

        if opt is None:
            raise Exception("opt not found.")
        if opt == "address":
            return tranaddress(chain, opttype, cursor, limit)
        elif opt == "record":
            return tranrecord(chain, sender, opttype, cursor, limit)
        elif opt == "records":
            return tranrecords(senders, opttype, cursor, limit)
        elif opt == "detail":
            return trandetail(dtype, version)
        elif opt == "workstate":
            return workstate()
        else:
            raise Exception(f"opt{opt} is invalid.")
    except Exception as e:
        ret = parse_except(e)
    return ret.to_json()



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
def tranaddress(chain, opttype = "swap", cursor = 0, limit = 99999999):
    try:
        logger.debug(f"get record address(chain = {chain}, opttype = {opttype}, cursor={cursor}, limit={limit})")

        check_chain(chain)

        rclient = requestclient("l2vrecord", get_proofdb("record"))
        ret = rclient.list_record_address_for_chain(chain, opttype, cursor = cursor, limit=limit)
        if ret.state != error.SUCCEED:
            raise f"get transaction record failed chain = {chain}"
        datas = {"cursor": ret.datas[0],\
                "count": len(ret.datas[1]), \
                "datas": [data[:0 - len(chain) -1 -len(opttype) -1] for data in ret.datas[1]]}
        ret = result(error.SUCCEED, "", datas)
    except Exception as e:
        ret = parse_except(e)
    return ret.to_json()

@app.route('/tranrecord/<string:chain>/<string:sender>/<int:cursor>/<int:limit>/', methods=['GET'])
def tranrecord(chain, sender, opttype = "swap", cursor = 0, limit = 99999999):
    try:
        logger.debug(f"get record(chain = {chain} sender={sender}, opttype = {opttype}, cursor={cursor}, limit={limit})")

        check_chain(chain)

        rclient = requestclient("l2vrecord", get_proofdb("record"))
        ret = rclient.get_transaction_record(sender, chain, opttype, cursor = cursor, limit=limit)
        if ret.state != error.SUCCEED:
            raise f"get transaction record failed.chain = {chain}, sender = {sender}, cursor={cursor}, limit={limit}"
        records = [json.loads(ret.datas[1][key]) for key in sorted(ret.datas[1].keys(), reverse = True)] 
        sorted_state = {"start":[], "cancel":[], "stop":[], "end":[]}

        for record in records:
            sorted_state[record.get("state")].append(record)
        records_ret = []
        records_ret.extend(sorted_state["start"])
        records_ret.extend(sorted_state["cancel"])
        records_ret.extend(sorted_state["stop"])
        records_ret.extend(sorted_state["end"])
        datas = {"cursor": ret.datas[0],\
                "count": len(ret.datas[1]), \
                "datas": records_ret\
                }
        ret = result(error.SUCCEED, "", datas)
    except Exception as e:
        ret = parse_except(e)
    return ret.to_json()

def tranrecords(senders, opttype = "swap", cursor = 0, limit = 99999999):
    try:
        logger.debug(f"get records(senders={senders}, opttype = {opttype}, cursor={cursor}, limit={limit})")

        rclient = requestclient("l2vrecord", get_proofdb("record"))
        ret = rclient.get_transaction_records(senders, opttype, cursor = cursor, limit=limit)
        if ret.state != error.SUCCEED:
            raise f"get transaction record failed.senders = {senders}, cursor={cursor}, limit={limit}"

        next_cursor = cursor + len(ret.datas)
        if next_cursor == cursor or len(ret.datas) < limit:
            next_cursor = 0
        datas = {"cursor": next_cursor, \
                "count": len(ret.datas), \
                "datas": [json.loads(record) for record in ret.datas] \
                }
        ret = result(error.SUCCEED, "", datas)
    except Exception as e:
        ret = parse_except(e)
    return ret.to_json()

def check_chain(chain):
    if chain is None or chain.upper() not in ("VIOLAS", "LIBRA", "BTC"):
        raise Exception(f"{chain} is invalid. must be [VIOLAS, LIBRA, BTC]")

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
