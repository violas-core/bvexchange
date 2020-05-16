#!/usr/bin/python3
import operator
import sys, os
import json
sys.path.append(os.getcwd())
sys.path.append("..")
import log
import log.logger
import traceback
import datetime
import requests
import stmanage
import comm
import comm.error
import comm.result
import comm.values
from comm.result import result, parse_except
from comm.error import error
from comm.functions import split_full_address, json_print
from baseobject import baseobject
from enum import Enum

#module name
name="violasproxy"

class violasproxy(baseobject):

    class opt(Enum):
        GET = 'get'
        SET = 'set'

    class opttype(Enum):
        B2V     = 'b2v'
        FILTER  = 'filter'
        MARK    = 'mark'
        BTCMARK = 'btcmark'
        BALANCE = 'balance'
        START   = 'start'
        END     = 'end'
        CANCEL  = 'cancel'

    def __init__(self, name, host, port = None, user = None, password = None, domain="violaslayer"):
        baseobject.__init__(self, name)

        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.domain = domain
        self._logger.debug(f"connect violas server(host={host}  port={port} domain={domain}")

    def convert_arg_to_url(self, args):
        url = ""
        for key in args.keys():
            url += f"&{key}={args[key]}"
        return url

    def create_opt_url(self, opt, opttype, **kvargs):
        url= ""
        if self.host[:4] == "http":
            url = self.host
        else:
            url = f"http://{self.host}"

        if self.port is not None:
            url += f":{self.port}/"
        else:
            if url[len(url)] != "/":
                url += "/"
            if self.domain is not None:
                url += self.domain

        url += f"?opt={opt.name.lower()}"
        url += f"&type={opttype.name.lower()}"
        url += self.convert_arg_to_url(kvargs)

        print(f"url:{url}")
        return url

    @property
    def domain(self):
        return self.__domain

    @domain.setter
    def domain(self, value):
        self.__domain = value

    @property 
    def user(self):
        return self.__user

    @user.setter
    def user(self, value):
        self.__user = value

    @property 
    def password(self):
        return self.__password

    @password.setter
    def password(self, value):
        self.__password = value

    @property 
    def host(self):
        return self.__host

    @host.setter
    def host(self, value):
        self.__host = value

    @property
    def port(self):
        return self.__port

    @port.setter
    def port(self, value):
        self.__port = value

    def disconn_node(self):
        pass

    def violas_listexproofforstate(self, state, extype, receiver, excluded = None):
        try:
            url = None
            if len(receiver) == 0:
                return result(error.ARG_INVALID, error.argument_invalid, "")

            if extype == comm.values.EX_TYPE_B2V and state in (self.opttype.START.value, self.opttype.END.value, self.opttype.CANCEL.value):
                url = self.create_opt_url(self.opt.GET, self.opttype.B2V, address=receiver, state=state, cursor = 0, limit=10)
            elif extype == comm.values.EX_TYPE_V2B and state == self.opttype.MARK:
                url = self.create_opt_url(self.opt.GET, self.opttype.MARK, address=receiver)
            else:
                return result(error.ARG_INVALID, f"(state={state}, extype={extype}, receiver={receiver})")

            datas = requests.get(url).json()
            ret = result()
            ret.load_json(datas)
            
        except Exception as e:
            ret = parse_except(e)
        return ret


    def stop(self):
        self.work_stop()

    def violas_listexproof(self, extype, cursor = 0, limit = 10):
        raise Exception("not support")

    def violas_isexproofcomplete(self, address, sequence):
        try:
            url = self.create_opt_url(self.opt.check, self.opttype.B2V, address=address, sequence=sequence)
            ret = requests.get(url).json()
            datas = requests.get(url).json()
            ret = result()
            ret.load_json(datas)
            self._logger.debug(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret


    def listexproofforb2v(self, cursor, limit = 1):
        try:
            datas = ""
            ret = result(error.SUCCEED, "", datas)
            self._logger.debug(f"result: {len(ret.datas)}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def violas_getexprooflatestindex(self, extype = comm.values.EX_TYPE_B2V):
        try:
            url = self.create_opt_url(self.opt.GET, self.opttype.B2V, datatype="version")
            ret = requests.get(url).json()
            datas = requests.get(url).json()
            ret = result()
            ret.load_json(datas)
            self._logger.debug(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def violas_sendexproofstart(self, fromaddress, toaddress, amount, vaddress, sequence, vtoken):#BTC
        try:
            datas = ""
            ret = result(error.SUCCEED, "", datas)
            self._logger.info(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def violas_sendexproofend(self, fromaddress, toaddress, vaddress, sequence, amount, version):#BTC
        try:
            datas = ""
            ret = result(error.SUCCEED, "", datas)
            self._logger.info(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def sendtoaddress(self, address, amount):#BTC
        try:
            datas = ""
            ret = result(error.SUCCEED, "", datas)
            self._logger.info(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret
   
    def violas_sendexproofmark(self, fromaddress, toaddress, toamount, vaddress, sequence, version):
        try:
            datas = ""
            ret = result(error.SUCCEED, "", datas)
            self._logger.info(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def generatetoaddress(self, count, address):
        raise Exception("not support")

    def listunspent(self, minconf = 1, maxconf = 9999999, addresses = None, include_unsafe = True, query_options = None):
        try:
            datas = ""
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def help(self):
        raise Exception("not support")

    def getwalletbalance(self):
        try:
            balance = -1
            ret = result(error.SUCCEED, "", balance)
            self._logger.debug(f"result: {ret.datas:.8f}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def getwalletaddressbalance(self, address):
        try:
            ret = result(error.SUCCEED, "", -1)
            self._logger.debug(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def violas_getexproofforaddress(self, address, version, extype = comm.values.EX_TYPE_V2B):
        try:
            datas = ""
            ret = result(error.SUCCEED, "", datas)
            self._logger.info(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def violas_getexproofforaddress(self, address, version, extype = comm.values.EX_TYPE_B2V):
        try:
            datas = ""
            ret = result(error.SUCCEED, "", datas)
            self._logger.info(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret


def main():
    try:
       receiver = "2N2YasTUdLbXsafHHmyoKUYcRRicRPgUyNB" #"2MxBZG7295wfsXaUj69quf8vucFzwG35UWh"
       #load logging
       conf = stmanage.get_btc_conn()
       print(conf)
       client = violasproxy(name, conf.get("host"), conf.get("port"), conf.get("user"), conf.get("password"), conf.get("domain", "violaslayer"))
       ret = client.violas_listexproofforstate("end", comm.values.EX_TYPE_B2V, receiver=receiver, excluded = None)
       json_print(ret.to_json())

       print("*"*30 + "get start ")
       client = violasproxy(name, conf.get("host"), conf.get("port"), conf.get("user"), conf.get("password"), conf.get("domain", "violaslayer"))
       ret = client.violas_listexproofforstate("start", comm.values.EX_TYPE_B2V, receiver=receiver, excluded = None)
       json_print(ret.to_json())


       ret = client.violas_getexprooflatestindex()
       json_print(ret.to_json())



    except Exception as e:
        parse_except(e)
    finally:
        print("end main")

if __name__ == "__main__":
    main()
