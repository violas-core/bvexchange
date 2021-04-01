#!/usr/bin/python3
import operator
import sys
import json
import os
import time
import types
sys.path.append(os.getcwd())
sys.path.append("..")
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))


def reponse(msg, conn = None, listener = None, **kwargs):
    return conn.send(f"{msg}") if not conn.closed else None

def is_func_or_method(func):
    return isinstance(func, types.MethodType) or isinstance(func, types.FunctionType)

def show_msg(msg, logger = None):
    if logger:
        logger.debug(msg)
    else:
        print(msg)

def call_shutdown(call):
    call()
    return False

def get_datas_from_cmd(arg):
    return arg() if is_func_or_method(arg) else arg

def parse_cmd(cmd, conn = None, listener = None, **kwargs):
    show_msg("received msg: {}".format(cmd), kwargs.get("logger"))
    if cmd in kwargs.keys():
        if cmd == "shutdown":
            reponse("shutdown...", conn)
            ret = get_datas_from_cmd(kwargs.get(cmd))
        else:
            reponse(get_datas_from_cmd(kwargs.get(cmd)), conn)
    else:
        return False
    return True


