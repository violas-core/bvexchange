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

import stmanage
from sms.smsclient import (
        smsclient
        )

from comm.values import (
        langtype
        )
from comm.parseargs import (
        parseargs
        )
def test_smsclient():
    client = smsclient("smsclient", 
            stmanage.get_sms_nodes(),
            stmanage.get_sms_templetes(),
            langtype.CH
            )

    #ret = client.send_message("+8618601999980", f"testclient:{time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime())}")
    books = stmanage.get_addressbook("msg")
    for item in books:
        ret = client.send_message(item["mobile"], f"vUSDT#Mint#v{item['mobile'][:8]}", item["lang"])
        print(ret)

def test_post():
    try:
        receiver = "+8618601999980"
        text = "test"
        url = f"http://13.68.141.242:8000/sms"
        message_templete = "【Violas】您有一条来自 {} 的数据请求需要处理 。"
        #data = {"receiver":receiver, "text":}
        data = {"receiver":receiver, "text":message_templete.format("test001")}
        print(f"url = {url} data = {data}")
        jret = requests.post(url = url, data = data)
        print(f"result : {jret.json()}")

    except Exception as e:
        print(e)

def init_stmanage():
    stmanage.set_conf_env("../bvexchange.toml")

if __name__ == "__main__":
    init_stmanage()
    pa = parseargs(globals())
    pa.test(sys.argv)

