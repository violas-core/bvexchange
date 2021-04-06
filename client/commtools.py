#!/usr/bin/python3
import operator
import sys
import json
import os
import time
import requests
import getopt
import readline
import signal
sys.path.append(os.getcwd())
sys.path.append("..")
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))


import stmanage
import log
import log.logger
from comm.result import result
from comm.parseargs import parseargs
from comm.functions import json_print
from lbcommunication import (
        comm_client ,
        )

from dataproof import (
        dataproof,
        )
#module name
name="commtools"
chain = "comm"
#load logging
logger = log.logger.getLogger(name) 

def parse_msg(datas, conn = None, listener = None, **kwargs):
    print(datas)
    json_print(result().loads(datas).to_json())

def show_call(func):
    def call_args(*args, **kwargs):
        print(f"args = {args}, kwargs = {kwargs}")
        return func(*args, **kwargs)
    return call_args

client = None
def get_client():
    global client
    if client and client.connected:
        return client
    listen = stmanage.get_cmd_listen()
    
    client = comm_client(listen.get("host"), listen.get("port"), listen.get("authkey"), call = parse_msg)
    return client


def shutdown():
    client = get_client()
    client.send("shutdown")
    client.close()

def get(itype):
    if not itype:
        return ["smods", "running"]
    client = get_client()
    client.send(itype)
    client.close()

def context(mod):
    client = get_client()
    client.send(f"context {mod}")
    client.close()

def dataproof(key):
    client = get_client()
    client.send(f"contexts {key}")
    client.close()

'''
*************************************************main oper*******************************************************
'''
def init_args(pargs):
    pargs.clear()
    pargs.append("help", "show arg list.")
    pargs.append("conf", "config file path name. default:bvexchange.toml, find from . and /etc/bridge/", True, "toml file", priority = 5)
    pargs.append(shutdown, "shutdown bridge server.")
    pargs.append(get, f"show info . itype : {get(None)}")
    pargs.append(context, f"show context info . mod: get it from running ")
    pargs.append(dataproof, f"show brigde contexts(dataproof) info . ")

def run(argc, argv, exit = True):
    try:
        if exit:
            logger.debug("start comm.main")
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
    if len(err_args) > 0:
        pargs.show_args()
        return

    names = [opt for opt, arg in opts]
    pargs.check_unique(names)

    global chain
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
            raise Exception(f"not found matched opt{opt}")
    if exit:
        logger.debug("end manage.main")

if __name__ == "__main__":
    run(len(sys.argv) - 1, sys.argv[1:])
