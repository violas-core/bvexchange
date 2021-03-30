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


from communication.client import (
        client
        )
def parse_msg(cmd, conn = None, listener = None, **kwargs):
    print("received msg: {}".format(cmd))


cli = client("127.0.0.1", 8888)
cli.start_connect(parse_msg)
time.sleep(1)
cli.send("msg 1")
time.sleep(1)
cli.send("msg 2")
time.sleep(1)
cli.send("shutdown")
cli.close()


