#!/usr/bin/python3
import operator
import sys
import json
import os
sys.path.append(os.getcwd())
sys.path.append("..")
import log
import log.logger
import traceback
import datetime
import sqlalchemy
import stmanage
import requests
import random
import comm
import comm.error
import comm.result
from comm.functions import json_print
from comm.result import result, parse_except
from comm.error import error
from db.dbb2v import dbb2v
from db.dbvfilter import dbvfilter
from db.dbvproof import dbvproof
from db.dbvbase import dbvbase
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from enum import Enum
from baseobject import baseobject
from vlsopt.violasclient import violasclient, violaswallet
import stmanage
import redis
import comm_funs
#module name
name="showworkenv"
wallet_name="vwallet"

logger = log.logger.getLogger(name)

def show_db():
    infos = []
    for idx in dbvbase.dbindex:
        dbconf = stmanage.get_db(idx.name.lower())
        db = dbvbase(name, dbconf.get("host"), dbconf.get("port"), dbconf.db_name_to_value(idx.name.lower()), dbconf.get(passwd))
        info = { \
                "mod_name" = db.get_mod_name(), \
                "latest_filter_ver": db.get_latest_filter_ver(), \
                "latest_saved_ver": db.get_latest_saved_ver(), \
                "min_valid_ver": db.get_min_valid_ver()
                "index":dbconf.db_name_to_value(idx.name.lower())
                "db":dbconf
                }
    json_print(infos)

def show_address():
    vclient = comm_funs.violasreg(name, stmanage.get_violas_nodes())
    wclient = comm_funs.walletreg(name, wallet_name)

    infos = {}
    #create vbtc module
    module = stmanage.get_module_address("v2b", "violas")
    assert module is not None and len(module) == 64, f"vbtc address[{module}] is not found"

    comm_funs.list_address_info(vclient, wclient, [module], ret = infos)

    #create vlibra module
    module = stmanage.get_module_address("v2l", "violas")
    assert module is not None and len(module) == 64, "vlibra module is not found"

    comm_funs.list_address_info(vclient, wclient, [module], ret = infos)

    #vbtc sender bind  module
    senders = stmanage.get_sender_address_list("b2v", "violas")
    assert senders is not None and len(senders) > 0, f"v2b senders[{senders}] not found."

    comm_funs.list_address_info(vclient, wclient, senders, ret = infos)

    #vlibra sender bind module
    senders = stmanage.get_sender_address_list("l2v", "violas")
    assert senders is not None and len(senders) > 0, f"v2l senders not found."

    comm_funs.list_address_info(vclient, wclient, senders, ret = infos)

    receivers = stmanage.get_receiver_address_list("v2l", "violas")
    assert receivers is not None and len(receivers) > 0, f"v2l receiver not found."

    comm_funs.list_address_info(vclient, wclient, receivers, ret = infos)

    receivers = stmanage.get_receiver_address_list("v2b", "violas")
    assert receivers is not None and len(receivers) > 0, f"v2b receiver not found."
    comm_funs.list_address_info(vclient, wclient, receivers, ret = infos)

    combin = stmanage.get_combine_address("v2b", "violas")
    assert combin is not None and len(combin) > 0, f"v2b combin not found or is invalid."
    comm_funs.list_address_info(vclient, wclient, [combin], ret = infos)

    logger.debug("start bind dtype = v2l chain = violas combin")
    combin = stmanage.get_combine_address("v2l", "violas")
    assert combin is not None and len(combin) == 64, f"v2l combin not found or is invalid."
    comm_funs.list_address_info(vclient, wclient, [combin], ret = infos)

    json_print(infos)

def show_config():
    stmanage.show()

def create_local_db_name(name, form_chain):
    return f"{from_chain}_{name}.db"

def get_local_state_info(db, states)
    info = {}
    for state in dbv2b.state:
        info[state.name] = dbv2b.query_state_count(state).datas
    return info

def get_local_v2b_info(name, chain):
    filename = create_local_db_name(name, chain)
    db = dbv2b(name, filename)
    infos = []
    infos.append(get_local_state_info(db, dbv2b.state))

def show_local_db():
    confs = [('violas', 'v2b'), ('violas', 'v2l'), ('btc', 'b2v'), ('libra', 'l2v')]
    infos = []
    for conf in confs:
        if conf[1] == "v2b":
            infos.extend(get_local_v2b_info(conf[1], conf[0]))
    json_print(infos)

def run():
if __name__ == "__main__":
    run()
