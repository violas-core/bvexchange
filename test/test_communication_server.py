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


from communication.server import (
        server
        )
def parse_msg(cmd, conn = None, listener = None, **kwargs):
    print("received msg: ".format(cmd))
    if cmd == "msg 1":
        print(f"send 11111111")
        conn.send("11111111")
    elif cmd == "msg 2":
        conn.send("22222222")
        print(f"send 2222222")
    else:
        conn.send(f"msg({cmd}) is invalid.")


svr = server("127.0.0.1", 8888)
svr.start_listen(parse_msg)

