#!/usr/bin/python3
import operator
import sys
import json
import os
import time
import requests
sys.path.append(os.getcwd())
sys.path.append("..")
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))


from lbcommunication import (
        comm_client as client,
        )
def parse_msg(cmd, conn = None, listener = None, **kwargs):
    print("received msg: {}".format(cmd))


cli = client("127.0.0.1", 8055, call = parse_msg)
#cli.start(parse_msg)
time.sleep(1)
#cli.send("smods")
time.sleep(1)
#cli.send("disconnect")
cli.send("shutdown")
time.sleep(1)
cli.close()


