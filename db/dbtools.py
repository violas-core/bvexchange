#!/usr/bin/python3
import operator
import os, sys, getopt
import json
sys.path.append(os.getcwd())
sys.path.append("..")
import log
import log.logger
import stmanage
import requests
import comm
import comm.error
import comm.result
import comm.values
from time import sleep
from comm.result import result, parse_except
from comm.error import error
from comm.amountconver import amountconver 
from db.dblocal import dblocal as localdb
from db.dbfunds import dbfunds as localfunds
from baseobject import baseobject
from comm.parseargs import parseargs
from enum import Enum
from comm.functions import (
        output_args,
        root_path,
        json_print,
        )

from dataproof import dataproof

name = "dbtools"
logger = log.logger.getLogger(name)
def get_localdb(id):
    return localdb(name, f"{id}.db", datas_path())

def datas_path():
    project_path = root_path()
    datas_path = os.path.join(project_path, dataproof.configs("datas_root_path")) 
    path = os.path.abspath(os.path.join(datas_path, "."))
    return path

def db_files_path():
    path = os.path.abspath(os.path.join(datas_path(), localdb.cache_name()))
    print(path)
    return path

def db_ids():
    file_names = os.listdir(db_files_path())
    ids = [name.replace(".db", "") for name in file_names]
    json_print(ids)
    return ids

def state_names():
    names = [state.name for state in localdb.state]
    print(names)
    return names

def update_localdb_tran_to_manualstop(db_id, tran_id, state, detail = json.dumps({"manual":"update state = stop"})):
    db_ids = db_ids()
    assert db_id in db_ids, f"{db_id} not in {db_ids}"

    db = get_localdb(db_id)
    if not db.has_info(tran_id):
        raise Exception(f"not found {tran_id}.")

    ret = db.query(tran_id);
    if len(ret.datas) != 1:
        raise Exception(f"not found {tran_id}.")

    data = ret.datas[0]
    old_detail = json.loads(data)
    old_detail.update(json.loads(detail))
    ret = db.update_state_commit(tran_id, localdb.state.MANUALSTOP, detail = old_detail)
    assert (ret.state == error.SUCCEED), "db error"

def datas_state_is_failed(db_id):
    states = [state for state in localdb.state \
                    if state not in [localdb.state.COMPLETE, \
                        localdb.state.VSUCCEED, \
                        localdb.state.SSUCCEED]]
    db = get_localdb(db_id)
    ret = db.get_record_from_localdb_with_state(states)
    assert (ret.state == error.SUCCEED), "db error"
    json_print(ret.datas)
    return ret

def datas_state_is_fixed(db_id, state):
    states = [localdb.state[state]]
    db = get_localdb(db_id)
    ret = db.get_record_from_localdb_with_state(states)
    assert (ret.state == error.SUCCEED), "db error"
    json_print(ret.datas)
    return ret




def init_args(pargs):
    pargs.clear()
    pargs.append("help", "show arg list.")
    pargs.append("chain", "work chain name(violas/libra/diem, default : violas). must be first argument", True, ["chain=violas"], priority = 10)
    pargs.append("conf", "config file path name. default:bvexchange.toml, find from . and /etc/bridge/", True, "toml file", priority = 5)
    pargs.append(db_ids, "show can use db ids")
    pargs.append(state_names, "show state names")
    pargs.append(db_files_path, "show db files path")
    pargs.append(update_localdb_tran_to_manualstop, "update transaction state")
    pargs.append(datas_state_is_failed, "show datas(state=xfailed)")
    pargs.append(datas_state_is_fixed, f"show datas(state={state_names()})")

def run(argc, argv, exit = True):
    global chain
    try:
        logger.debug("start dbclienttools")
        pargs = parseargs(exit = exit)
        init_args(pargs)
        if pargs.show_help(argv):
            return 
        opts, err_args = pargs.getopt(argv)
    except getopt.GetoptError as e:
        logger.error(e)
        if exit:
            sys.exit(2)
        return 
    except Exception as e:
        logger.error(e)
        if exit:
            sys.exit(2)
        return

    #argument start for --
    if err_args and len(err_args) > 0:
        pargs.show_args()
        return

    names = [opt for opt, arg in opts]
    pargs.check_unique(names)
    
    for opt, arg in opts:

        arg_list = []
        if len(arg) > 0:
            count, arg_list = pargs.split_arg(opt, arg)

            print("opt = {}, arg = {}".format(opt, arg_list))
        if pargs.is_matched(opt, ["help"]):
            pargs.show_args()
            return
        elif pargs.is_matched(opt, ["conf"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            stmanage.set_conf_env(arg_list[0])
        elif pargs.has_callback(opt):
            pargs.callback(opt, *arg_list)
        else:
            raise Exception(f"not found matched opt: {opt}")


    logger.debug("end manage.main")

if __name__ == "__main__":
    run(len(sys.argv) - 1, sys.argv[1:])
