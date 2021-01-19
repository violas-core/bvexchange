#!/usr/bin/python3
import operator
import sys
import json
import os
sys.path.append(os.getcwd())
sys.path.append("..")
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../lbviolasclient"))

import requests
from comm.error import error
from comm.result import result, parse_except
from baseobject import baseobject
from dataproof import dataproof
from comm.functions import (
        output_args
        )
from comm.values import (
        langtype,
        )
class smsclient(baseobject):
    REPLACE_DATA = "ssss"
    def __init__(self, name, nodes, templetes, lang = "ch"):
        baseobject.__init__(self, name)
        self.__client = None
        self.__node = None
        self.__templetes = templetes
        if nodes is not None:
            ret = self.conn_node(nodes)
            if not ret:
                raise Exception(f"connect sms node failed.")
        self.select_templete(lang)

    def reset_templete(self):
        self.__templete = None

    def select_templete(self, lang):
        self.reset_templete()

        lang = self.to_str(lang)

        for item in self.__templetes:
            if item.get("lang", "") == lang:
                self.__templete = item
                self.__templete["data"].index(item.get("replace", self.REPLACE_DATA))
                return True
        raise ValueError(f"not found {lang} templete. check args and {self.__templetes}")

    def conn_node(self, nodes):
        self.__url = None
        for node in nodes:
            url = node.get("host")
            host = node.get("host")
            port = node.get("port")
            subdomain = node.get("subdomain")
            if "://" not in host:
                url = f"http://{host}"
            if port is not None:
                url += f":{port}"
            if subdomain is not None:
                url += f"/{subdomain}"
            self.__url = url
        return self.__url is not None 

    def send_message(self, mobile, message):
        try:
            ret = result(error.FAILED, "", "")
            message = self.__templete["data"].replace(self.__templete.get("replace", self.REPLACE_DATA), message)
            data = {"receiver":mobile, "text":message}
            print(data)
            response = requests.post(url = self.__url, data = data)
            if response is not None:
                jret = response.json()
                if jret["code"] == 200:
                    ret = result(error.SUCCEED, jret["msg"], True)
                else:
                    ret = result(error.SUCCEED, jret["msg"], False)
        except Exception as e:
            ret = parse_except(e)
        return ret

