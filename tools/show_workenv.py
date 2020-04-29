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
import comm.values
from comm.functions import json_print
from comm.result import result, parse_except
from comm.error import error
from db.dbb2v import dbb2v
from db.dbv2b import dbv2b
from db.dbl2v import dbl2v
from db.dbvfilter import dbvfilter
from db.dbvproof import dbvproof
from db.dbvbase import dbvbase
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from enum import Enum
from baseobject import baseobject
from vlsopt.violasclient import violasclient, violaswallet
import stmanage
import redis
from tools import comm_funs
#module name
name="showworkenv"
wallet_name="vwallet"
VIOLAS_ADDRESS_LEN = comm.values.VIOLAS_ADDRESS_LEN
logger = log.logger.getLogger(name)

def show_db():
    infos = {}
    for idx in dbvbase.dbindex:
        dbconf = stmanage.get_db(idx.name.lower())
        db = dbvbase(name, dbconf.get("host"), dbconf.get("port"), idx.name.lower(), dbconf.get("password"))
        info = { \
                "mod_name" : db.get_mod_name().datas, \
                "latest_filter_ver": db.get_latest_filter_ver().datas, \
                "latest_saved_ver": db.get_latest_saved_ver().datas, \
                "min_valid_ver": db.get_min_valid_ver().datas, \
                "index": idx.value, \
                "db":dbconf, \
                }
        infos[idx.name.lower()] = info
    json_print(infos)

def show_address():
    vclient = comm_funs.violasreg(name, stmanage.get_violas_nodes())
    wclient = comm_funs.walletreg(name, wallet_name)

    infos = {}
    #create vbtc module
    vbtc_module = stmanage.get_module_address("v2b", "violas")
    assert vbtc_module is not None and len(vbtc_module) in VIOLAS_ADDRESS_LEN, f"vbtc address[{vbtc_module}] is not found"

    comm_funs.list_address_info(vclient, wclient, [vbtc_module], vbtc_module, ret = infos)

    #create vlibra module
    vlibra_module = stmanage.get_module_address("v2l", "violas")
    assert vlibra_module is not None and len(vlibra_module) in VIOLAS_ADDRESS_LEN, "vlibra module is not found"

    comm_funs.list_address_info(vclient, wclient, [vlibra_module], vlibra_module, ret = infos)

    #vbtc sender bind  module
    senders = stmanage.get_sender_address_list("b2v", "violas")
    assert senders is not None and len(senders) > 0, f"v2b senders[{senders}] not found."

    comm_funs.list_address_info(vclient, wclient, senders, vbtc_module, ret = infos)

    #vlibra sender bind module
    senders = stmanage.get_sender_address_list("l2v", "violas")
    assert senders is not None and len(senders) > 0, f"v2l senders not found."

    comm_funs.list_address_info(vclient, wclient, senders, vlibra_module, ret = infos)

    receivers = stmanage.get_receiver_address_list("v2l", "violas")
    assert receivers is not None and len(receivers) > 0, f"v2l receiver not found."

    comm_funs.list_address_info(vclient, wclient, receivers, vlibra_module, ret = infos)

    receivers = stmanage.get_receiver_address_list("v2b", "violas")
    assert receivers is not None and len(receivers) > 0, f"v2b receiver not found."
    comm_funs.list_address_info(vclient, wclient, receivers, vbtc_module, ret = infos)

    combin = stmanage.get_combine_address("v2b", "violas")
    assert combin is not None and len(combin) > 0, f"v2b combin not found or is invalid."
    comm_funs.list_address_info(vclient, wclient, [combin], vbtc_module, ret = infos)

    logger.debug("start bind dtype = v2l chain = violas combin")
    combin = stmanage.get_combine_address("v2l", "violas")
    assert combin is not None and len(combin) in VIOLAS_ADDRESS_LEN, f"v2l combin not found or is invalid."
    comm_funs.list_address_info(vclient, wclient, [combin], vlibra_module, ret = infos)

    #start get libra address info
    '''
    logger.debug("********start get libra chain address info********")
    linfos = {}
    lclient = comm_funs.violasreg(name, stmanage.get_libra_nodes(), chain = "libra")
    lwclient = comm_funs.walletreg(name, wallet_name, chain = "libra")
    #vbtc sender bind  module
    senders = stmanage.get_sender_address_list("v2l", "libra")
    assert senders is not None and len(senders) > 0, f"v2l senders[{senders}] not found."

    comm_funs.list_address_info(lclient, lwclient, senders, None, ret = linfos)

    logger.debug("********libra chain address info********")
    json_print(linfos)

    '''

    logger.debug("********violas chain address info********")
    json_print(infos)

def show_config():
    infos = stmanage.get_conf()
    json_print(infos)

def __create_local_db_name(name, from_chain):
    return f"{from_chain}_{name}.db"

def __get_local_state_info(db, states):
    info = {}
    for state in db.state:
        info[state.name] = db.query_state_count(state).datas
    return info

def get_local_v2b_info(name, chain):
    filename = __create_local_db_name(name, chain)
    db = dbv2b(name, filename)
    return __get_local_state_info(db, db.state)

def get_local_b2v_info(name, chain):
    filename = __create_local_db_name(name, chain)
    db = dbb2v(name, filename)
    return __get_local_state_info(db, db.state)

def get_local_exlv_info(name, chain):
    filename = __create_local_db_name(name, chain)
    db = dbl2v(name, filename)
    return __get_local_state_info(db, db.state)

def show_local_db():
    confs = [('violas', 'v2b'), ('violas', 'v2l'), ('btc', 'b2v'), ('libra', 'l2v')]
    infos = {}
    for conf in confs:
        if conf[1] == "v2b":
            infos[conf[1]] = get_local_v2b_info(conf[1], conf[0])
        elif conf[1] in ['v2l', 'l2v']:
            infos[conf[1]] = get_local_exlv_info(conf[1], conf[0])
        elif conf[1] == "b2v":
            infos[conf[1]] = get_local_b2v_info(conf[1], conf[0])
    json_print(infos)

class work_mod(Enum):
    CONF      = 0
    LDB       = 1
    RDB       = 2
    ADDR      = 3

def list_valid_mods():
    valid_mods = ["all"]
    for mod in work_mod:
        valid_mods.append(mod.name.lower())
    return valid_mods

def start(work_mods):
    if work_mods.get(work_mod.LDB.name, False):
        show_local_db()

    if work_mods.get(work_mod.RDB.name, False):
        show_db()

    if work_mods.get(work_mod.CONF.name, False):
        show_config()

    if work_mods.get(work_mod.ADDR.name, False):
        show_address()


def run(mods):
    valid_mods = list_valid_mods()
    for mod in mods:
        if mod is None or mod not in valid_mods:
            raise Exception(f"mod({mod}) is invalid {valid_mods}.")

    work_mods = {}
    for mod in mods:
        work_mods[mod.upper()] = True
        if mod == "all":
            for wm in work_mod:
                work_mods[wm.name.upper()] = True
            break

    start(work_mods)

def main(argc, argv):

    try:
        if argc < 1:
            raise Exception(f"argument is invalid. args:{list_valid_mods()}")
        run(argv)
    except Exception as e:
        parse_except(e)
    finally:
        logger.critical("main end")

if __name__ == "__main__":
    main(len(sys.argv) - 1, sys.argv[1:])
