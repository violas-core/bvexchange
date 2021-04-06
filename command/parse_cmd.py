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

from comm.result import (
        result
        )

from comm.error import (
        error
        )

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

def get_datas_from_cmd(cmd, args):
    try:
        ret = result(error.SUCCEED, datas = cmd(*args) if is_func_or_method(cmd) else cmd)
    except Exception as e:
        ret = result(error.FAILED, e)
    return ret


def split_cmd_args(cmd):
    if cmd:
        cmd.strip()
        fields = cmd.split(" ")
        return (fields[0], fields[1:])
    return (None, [])

def parse_cmd(cmd, conn = None, listener = None, **kwargs):
    show_msg("received msg: {}".format(cmd), kwargs.get("logger"))

    cmd, args = split_cmd_args(cmd)
    print(f"cmd = {cmd} args={args}")
    if cmd in kwargs.keys():
        if cmd == "shutdown":
            reponse("shutdown...", conn)
            ret = get_datas_from_cmd(kwargs.get(cmd), args)
        else:
            reponse(get_datas_from_cmd(kwargs.get(cmd), args), conn)
    else:
        return False
    return True


