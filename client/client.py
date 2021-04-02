#!/usr/bin/python3
import operator
import sys
import json
import os
import time
import requests
import getopt
sys.path.append(os.getcwd())
sys.path.append("..")
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))


import stmanage
import log
import log.logger
from comm.parseargs import parseargs
from comm.functions import json_print
from lbcommunication import (
        comm_client as client,
        )

def show_call(func):
    def call_args(*args, **kwargs):
        print(f"args = {args}, kwargs = {kwargs}")
        return func(*args, **kwargs)
    return call_args

def bridge():
    def parse_msg(cmd, conn = None, listener = None, **kwargs):
        print("received msg: {}".format(cmd))
    
    
    cli = client("127.0.0.1", 8055, call = parse_msg)
    #cli.start(parse_msg)
    time.sleep(1)
    cli.send("smods")
    time.sleep(1)
    #cli.send("disconnect")
    cli.send("running")
    cli.send("shutdown")
    time.sleep(1)
    cli.close()


def violas():
    show_module_info("violas")
    from vlsopt import violastools
    violas.chain = "violas"
    while True:
        cmd = input("client.violas$: ")
        state, cmd, args = parse_cmd(cmd)
        argv = [cmd] + args
        violastools.run(len(argv), argv, exit = False)


def libra():
    show_module_info("libra")
    from vlsopt import violastools
    violas.chain = "libra"
    violastools.run(0, [])

def ethereum():
    show_module_info("ethereum")
    from vlsopt import violastools
    violas.chain = "ethereum"
    violastools.run(0, [])

def init_args(pargs):
    pargs.clear()
    pargs.append("help", "show arg list.")
    pargs.append("conf", "config file path name. default:bvexchange.toml, find from . and /etc/bridge/", True, "toml file", priority = 5)
    pargs.append(use, "select module")

def show_module_info(module):
    print(f"switch to {module}")

def use(module = None):
    support_module = ("violas", "libra", "ethereum", "btc", "bridge")
    if not module or module not in support_module:
        return support_module

    globals()[module]()

def exit():
    sys.exit()

def process_args():
    pargs = parseargs(exit = False)
    pargs.append("help", "show arg list.")
    pargs.append(use, f"select module, args: {use()}")
    pargs.append(exit, f"exit client")

    return pargs

def help(pargs, args = None):
    if args is None or len(args) == 0:
        pargs.show_args()
    else:
        pargs.show_help(["help", args[0]])

def parse_cmd(cmd):
    cmd = cmd
    args = None
    state = True
    try:
        cmd_arg = cmd.split(' ')
        cmd = cmd_arg[0]
        args = cmd_arg[1:]
        print(f"cmd = {cmd} args = {args}")
    except Exception as e:
        state = False
        pass



    return (state, cmd, args)

def process():
    pargs = process_args()
    while True:
        cmd = input("client$: ")
        state, cmd, args = parse_cmd(cmd)
        if state:
            if cmd == "help":
                help(pargs, args)
                continue
            if pargs.has_callback(cmd):
                pargs.callback(cmd, *args)


def main(argc, argv):
    try:
        pargs = parseargs()
        init_args(pargs)
        opts, err_args = pargs.getopt(argv)
    except getopt.GetoptError as e:
        logger.error(e)
        sys.exit(2)
    except Exception as e:
        logger.error(e)
        sys.exit(2)

    #argument start for --
    if len(err_args) > 0:
        pargs.show_args()

    names = [opt for opt, arg in opts]
    pargs.check_unique(names)
    
    for opt, arg in opts:

        arg_list = []
        if len(arg) > 0:
            count, arg_list = pargs.split_arg(opt, arg)

            print("opt = {}, arg = {}".format(opt, arg_list))
        if pargs.is_matched(opt, ["help"]):
            pargs.show_args()
        elif pargs.is_matched(opt, ["conf"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            stmanage.set_conf_env(arg_list[0])

    process()


    logger.debug("end manage.main")

if __name__ == "__main__":
    main(len(sys.argv) - 1, sys.argv[1:])

