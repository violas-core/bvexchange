#!/usr/bin/python3
import operator
import sys
import json
import os
import time
sys.path.append(os.getcwd())
sys.path.append("..")
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))


def reponse(msg, conn = None, listener = None, **kwargs):
    return conn.send(f"{msg}")

def show_msg(msg, logger = None):
    if logger:
        logger.debug(msg)
    else:
        print(msg)

def parse_cmd(cmd, conn = None, listener = None, **kwargs):
    show_msg("received msg: {}".format(cmd), kwargs.get("logger"))
    support_mods = kwargs.get("support_mods", [])
    if cmd == "smods":
        reponse(support_mods, conn)
    elif cmd == "shutdown":
        kwargs.get(cmd)()
        reponse("shutdown...", conn)
        return False

    elif cmd == "msg 2":
        reponse("22222222", conn)
    else:
        return False
    return True


