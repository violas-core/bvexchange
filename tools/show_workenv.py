#!/usr/bin/python3
import operator
import sys
import json
import os
sys.path.append(os.getcwd())
sys.path.append("..")
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
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
import stmanage
import redis
from comm.parseargs import parseargs
from comm.values import (
        dbindexbase as dbindex,
        trantypebase as trantype,
        datatypebase as datatype
        )

from comm.functions import (
        json_print, 
        human_address
        )
from comm.result import result, parse_except
from comm.error import error
from db.dblocal import dblocal as localdb
from db.dbvfilter import dbvfilter
from db.dbvproof import dbvproof
from db.dbvbase import dbvbase
from enum import Enum
from baseobject import baseobject
from vlsopt.violasclient import violasclient, violaswallet
from ethopt.ethclient import (
        ethclient,
        ethwallet
        )

from dataproof import dataproof
from tools import comm_funs
#module name
name="showworkenv"
wallet_name="vwallet"
VIOLAS_ADDRESS_LEN = comm.values.VIOLAS_ADDRESS_LEN
logger = log.logger.getLogger(name)

def get_ethclient(usd_erc20 = True):

    client = ethclient(name, stmanage.get_eth_nodes(), "ethereum")
    client.load_vlsmproof(stmanage.get_eth_token("vlsmproof")["address"])
    if usd_erc20:
        tokens = client.get_token_list().datas
        logger.debug(f"support tokens: {tokens}")
        for token in tokens:
            client.load_contract(token)
    return client
    
def get_ethwallet():
    return ethwallet(name, dataproof.wallets("ethereum"), "ethereum")

def show_db():
    infos = {}
    for idx in dbindex:
        dbconf = stmanage.get_db(idx.name.lower())
        db = dbvbase(name, dbconf.get("host"), dbconf.get("port"), idx.name.lower(), dbconf.get("password"))
        info = { \
                "mod_name" : db.get_mod_name().datas, \
                "latest_filter_ver": db.get_latest_filter_ver().datas, \
                "latest_saved_ver": db.get_latest_saved_ver().datas, \
                "min_valid_ver": db.get_min_valid_ver().datas, \
                "index": idx.value, \
                #"db":dbconf, \
                }
        infos[idx.name.lower()] = info
    json_print(infos)
    return infos

def show_address():
    vclient = comm_funs.violasreg(name, stmanage.get_violas_nodes())
    vwclient = comm_funs.walletreg(name, wallet_name)

    lclient = comm_funs.violasreg(name, stmanage.get_libra_nodes(), chain = "libra")
    lwclient = comm_funs.walletreg(name, wallet_name, chain = "libra")

    eclient = get_ethclient()
    ewclient = get_ethwallet()


    cclients = {"violas":vclient, "libra":lclient, "ethereum": eclient}
    wclients = {"violas":vwclient, "libra":lwclient, "ethereum": ewclient}
    infos = {}

    dtypes = stmanage.get_support_dtypes()
    for dtype in dtypes:
        from_chain, to_chain = stmanage.get_exchang_chains(dtype)

        cclient = cclients.get(to_chain)
        wclient = wclients.get(to_chain)
        if not cclient or not wclient or not to_chain:
            logger.debug(f"not found {to_chain} in {dtype}, continue next...")
            continue

        logger.debug(f"get chain = {to_chain}  dtype = {dtype} info.")
        senders = stmanage.get_sender_address_list(dtype, to_chain)
        comm_funs.list_address_info(cclient, wclient, senders, ret = infos)

        combin = stmanage.get_combine_address(dtype, to_chain)
        if not combin:
           continue 
        comm_funs.list_address_info(cclient, wclient, [combin], ret = infos)


    for dtype in dtypes:
        from_chain, to_chain = stmanage.get_exchang_chains(dtype)

        cclient = cclients.get(from_chain)
        wclient = wclients.get(from_chain)
        if not cclient or not wclient or not to_chain:
            logger.debug(f"not found {from_chain}, continue next...")
            continue

        logger.debug(f"get chain = {from_chain}  dtype = {dtype} info.")
        if dtype == "e2vm":
            receivers = [stmanage.get_map_address(dtype, from_chain)]
        else:
            receivers = stmanage.get_receiver_address_list(dtype, from_chain)

        comm_funs.list_address_info(cclient, wclient, receivers, ret = infos)

        #uniswap use combine
        combin = stmanage.get_combine_address(dtype, from_chain)
        if not combin:
           continue 
        comm_funs.list_address_info(cclient, wclient, [combin], ret = infos)

    #funds
    receivers = stmanage.get_receiver_address_list("funds", trantype.VIOLAS)
    comm_funs.list_address_info(cclient, wclient, receivers, ret = infos)

    #start get libra address info

    logger.debug("********violas chain address info********")
    json_print(infos)

    return infos

def show_config():
    infos = stmanage.get_conf()
    json_print(infos)
    return infos

def __create_local_db_name(name, from_chain, path = ""):
    return f"{path}{from_chain}_{name}.db"

def __get_local_state_info(db, states):
    info = {}
    if not db.init_state:
        return info

    for state in db.state:
        count = db.query_state_count(state).datas
        if count > 0:
            info[state.name] = count
    return info

def get_local_info(name, chain):
    filename = __create_local_db_name(name, chain)

    db = localdb(name, filename, False)
    return __get_local_state_info(db, db.state)

def show_local_db():
    confs = []
    for key in stmanage.get_support_mods_info():
        if key.startswith("v"):
            confs.append(("violas", key))
        elif key.startswith("l"):
            confs.append(("libra", key))
        elif key.startswith("b"):
            confs.append(("btc", key))
        elif key.startswith("e"):
            confs.append(("ethereum", key))
    infos = {}
    for conf in confs:
        infos[conf[1]] = get_local_info(conf[1], conf[0])
    json_print(infos)
    return infos

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
        try:
           show_db()
        except Exception as e:
            pass

    if work_mods.get(work_mod.CONF.name, False):
        show_config()

    if work_mods.get(work_mod.ADDR.name, False):
        show_address()

def show(mods):
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

def init_args(pargs):
    pargs.clear()
    pargs.append("help", "show arg list.")
    pargs.append("conf", "config file path name. default:bvexchange.toml, find from . and /etc/bvexchange/", True, "toml file", priority = 5)
    pargs.append("vwallet", "inpurt wallet file or mnemonic", True, "file name/mnemonic", priority = 13, argtype = parseargs.argtype.STR)
    pargs.append("ewallet", "inpurt wallet file or mnemonic", True, "file name/mnemonic", priority = 13, argtype = parseargs.argtype.STR)
    pargs.append("show", f"show env info args = {list_valid_mods()}.", True, list_valid_mods())


def main(argc, argv):

    try:
        pargs = parseargs(exit = exit)
        init_args(pargs)
        if pargs.show_help(argv):
            return
        opts, err_args = pargs.getopt(argv)
    except Exception as e:
        logger.error(e)
        if exit:
            sys.exit(2)
        return

    #argument start for --
    if len(err_args) > 0:
        pargs.show_args()
        return 

    names = [opt for opt, arg in opts]
    pargs.check_unique(names)

    for opt, arg in opts:

        arg_list = []
        if len(arg) > 0:
            count, arg_list = pargs.split_arg(opt, arg)

        if pargs.is_matched(opt, ["conf"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            stmanage.set_conf_env(arg_list[0])
        elif pargs.is_matched(opt, ["vwallet"]):
            if not pargs.exit_check_opt_arg(opt, arg, 1):
                return
            dataproof.wallets.update_wallet("violas", arg_list[0])
        elif pargs.is_matched(opt, ["ewallet"]):
            if not pargs.exit_check_opt_arg(opt, arg, 1):
                return
            dataproof.wallets.update_wallet("ethereum", arg_list[0])
        elif pargs.is_matched(opt, ["show"]):
            if not pargs.exit_check_opt_arg_min(opt, arg, 1):
                return
            show(arg_list)
            return
        elif pargs.has_callback(opt):
            pargs.callback(opt, *arg_list)
        else:
            raise Exception(f"not found matched opt: {opt}")

if __name__ == "__main__":
    main(len(sys.argv) - 1, sys.argv[1:])
