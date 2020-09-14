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
from enum import Enum, auto
from btc.btcwallet import btcwallet
from comm.values import autoname 
#module name
name="violasproxy"

class violasproxy(baseobject):

    class opt(autoname):
        GET = auto()
        SET = auto()
        CHECK = auto()

    class txstate(autoname):
        START   = auto()
        CANCEL  = auto()
        END     = auto()
        STOP    = auto()
        BTCMARK = auto()
        MARK    = auto()

    class opttype(autoname):
        BTCMARK = auto() # btc mark
        MARK    = auto() # mark
        B2VM    = auto() 
        V2B     = auto()
        V2BM    = auto()
        B2VUSD  = auto() 
        B2VEUR  = auto() 
        B2VSGD  = auto() 
        B2VGBP  = auto() 
        B2LUSD  = auto() 
        B2LEUR  = auto() 
        B2LSGD  = auto() 
        B2LGBP  = auto() 
        
        FILTER  = auto()
        BALANCE = auto()
        LISTUNSPENT = auto()
        PROOF       = auto()
        PROOFBASE   = auto()
        FIXTRAN     = auto()

    def __init__(self, name, host, port = None, user = None, password = None, domain="violaslayer", walletname="bwallet"):
        baseobject.__init__(self, name)

        self.user = str(user)
        self.password = str(password)
        self.host = str(host)
        self.port = port
        self.domain = str(domain)
        self.wallet = btcwallet(walletname)
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

        return url

    @property
    def wallet(self):
        return self.__wallet

    @wallet.setter
    def wallet(self, value):
        self.__wallet = value

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

    def run_request(self, url):
        ret = requests.get(url)
        if ret is None:
            raise Exception(f"execute request failed. {ret.text}")

        datas = ret.json()
        state = datas.get("state")
        if state.upper() != "SUCCEED":
            raise Exception(datas.get("message"))
        return datas.get("datas")

    def is_excluded(self, proof, excludeds):
        if excludeds is None:
            return False

        for excluded in excludeds:
            if proof.get("address") == excluded.get("address", "") and \
                    int(proof.get("sequence")) == int(excluded.get("sequence")):
                return True
        return False

    @property
    def valid_state(self):
        return [self.txstate.START.value, self.txstate.CANCEL.value, self.txstate.END.value, self.txstate.STOP.value]

    @property
    def valid_swap_type(self):
        return (comm.values.EX_TYPE_PROOF)

    def violas_listexproofforstate(self, opttype, state, extype, receiver, excluded = None):
        url = None
        if len(receiver) == 0:
            raise Exception(f"receiver is empty")

        if extype in self.valid_swap_type and state in self.valid_state:
            url = self.create_opt_url(self.opt.GET, self.opttype[opttype.upper()], address=receiver, state=state, cursor = 0, limit=10)
        elif extype == comm.values.EX_TYPE_MARK and state == self.opttype.MARK:
            url = self.create_opt_url(self.opt.GET, self.opttype.MARK, address=receiver)
        else:
            raise Exception(f"(state={state}, extype={extype}, receiver={receiver})")

        datas = requests.get(url).json().get("datas")

        if datas is None:
            return []

        return [data for data in datas if not self.is_excluded(data, excluded)]

    def stop(self):
        self.work_stop()

    def violas_listexproof(self, cursor = 0, limit = 10):
        url = None
        url = self.create_opt_url(self.opt.GET, self.opttype.PROOFBASE, cursor=cursor, limit=limit)
        return self.run_request(url)

    def violas_gettransaction(self, tranid):
        url = None
        url = self.create_opt_url(self.opt.GET, self.opttype.FIXTRAN, tranid = tranid)
        return self.run_request(url)

    def violas_isexproofcomplete(self, opttype, address, sequence):
        url = self.create_opt_url(self.opt.CHECK, self.opttype[opttype.upper()], address=address, sequence=sequence)
        return self.run_request(url)

    def violas_getexprooflatestindex(self, extype = comm.values.EX_TYPE_PROOF):
        url = self.create_opt_url(self.opt.GET, self.opttype.PROOFBASE, datatype="version")
        ret = requests.get(url).json()
        return self.run_request(url)

    def get_privkeys(self, address, privkeys = None):
        if privkeys is None:
            privkey = self.wallet.get_privkey(address)
            if privkey is None or len(privkey) == 0:
                raise Exception(f"{address}'s privkey is not found. address:{address}")
            privkeys = [privkey]
        if privkeys is None or len(privkeys) == 0:
            raise Exception(f"{address}'s privkey is not found. address:{address}")

        return privkeys

    def violas_sendexproofstart(self, opttype, fromaddress, toaddress, amount, vaddress, sequence, vtoken, fromprivkeys = None):#BTC

        fromprivkeys = self.get_privkeys(fromaddress, fromprivkeys)
        url = self.create_opt_url(self.opt.SET, self.opttype[opttype.upper()], state="start", \
                fromaddress=fromaddress, toaddress=toaddress, toamount=amount, \
                vreceiver=vaddress, sequence=sequence, module=vtoken, fromprivkeys=json.dumps(fromprivkeys))
        return self.run_request(url)

    def violas_sendexproofend(self, opttype, fromaddress, toaddress, vaddress, sequence, amount, version, fromprivkeys = None):#BTC
        fromprivkeys = self.get_privkeys(fromaddress, fromprivkeys)
        url = self.create_opt_url(self.opt.SET, self.opttype[opttype.upper()], state="end", \
                fromaddress=fromaddress, toaddress=toaddress, toamount=0, \
                vreceiver=vaddress, sequence=sequence, amount = amount, version=version, fromprivkeys=json.dumps(fromprivkeys))
        return self.run_request(url)

    def violas_sendexproofcancel(self, opttype, fromaddress, toaddress, amount, vaddress, sequence, fromprivkeys = None):#BTC
        fromprivkeys = self.get_privkeys(fromaddress, fromprivkeys)
        url = self.create_opt_url(self.opt.SET, self.opttype[opttype.upper()], state="cancel", \
                fromaddress=fromaddress, toaddress=toaddress, toamount=0, \
                vreceiver=vaddress, sequence=sequence, fromprivkeys=json.dumps(fromprivkeys))
        return self.run_request(url)

    def violas_sendexproofstop(self, opttype, fromaddress, toaddress, amount, vaddress, sequence, withgas=False, fromprivkeys = None):#BTC
        fromprivkeys = self.get_privkeys(fromaddress, fromprivkeys)
        url = self.create_opt_url(self.opt.SET, self.opttype[opttype.upper()], state="stop", \
                fromaddress=fromaddress, toaddress=toaddress, toamount=amount, \
                vreceiver=vaddress, sequence=sequence, withgas=withgas, fromprivkeys=json.dumps(fromprivkeys))
        return self.run_request(url)

    def sendtoaddress(self, address, amount):#BTC
        raise Exception("not support")
   
    def violas_sendexproofmark(self, fromaddress, toaddress, toamount, vaddress, sequence, version, fromprivkeys = None):
        fromprivkeys = self.get_privkeys(fromaddress, fromprivkeys)
        url = self.create_opt_url(self.opt.SET, self.opttype.MARK, state="mark", \
                fromaddress=fromaddress, toaddress=toaddress, toamount=toamount, \
                vreceiver=vaddress, sequence=sequence, version=version, fromprivkeys=json.dumps(fromprivkeys))
        return self.run_request(url)

    def generatetoaddress(self, count, address):
        raise Exception("not support")

    def listunspent(self, minconf = 1, maxconf = 9999999, addresses = None, include_unsafe = True, query_options = None):
        url = self.create_opt_url(self.opt.GET, self.opttype.LISTUNSPENT, address=json.dumps(addresses), minconf = minconf, maxconf=maxconf)
        return self.run_request(url)

    def help(self):
        raise Exception("not support")

    def getwalletbalance(self):
        raise Exception("not support")

    def getwalletinfo(self):
        raise Exception("not support")

    def getwalletaddressbalance(self, address, minconf=1, maxconf=99999999):
        url = self.create_opt_url(self.opt.GET, self.opttype.BALANCE, address=address, minconf = minconf, maxconf=maxconf)
        return self.run_request(url)

def main():
    try:
       receiver = "2N2YasTUdLbXsafHHmyoKUYcRRicRPgUyNB" #"2MxBZG7295wfsXaUj69quf8vucFzwG35UWh"
       #load logging
       stmanage.set_conf_env_default()
       conf = stmanage.get_btc_conn()
       print(conf)
       client = violasproxy(name, conf.get("host"), conf.get("port"), conf.get("user"), conf.get("password"), conf.get("domain", "violaslayer"))
       ret = client.violas_listexproofforstate("b2vusd","end", comm.values.EX_TYPE_PROOF, receiver=receiver, excluded = None)
       json_print(ret)

       print("*"*30 + "get start ")
       client = violasproxy(name, conf.get("host"), conf.get("port"), conf.get("user"), conf.get("password"), conf.get("domain", "violaslayer"))
       ret = client.violas_listexproofforstate("b2vusd", "start", comm.values.EX_TYPE_PROOF, receiver=receiver, excluded = None)
       json_print(ret)


       print("*"*30 + "get proof latest index")
       ret = client.violas_getexprooflatestindex("b2vusd")
       json_print(ret)


       print("*"*30 + "get proof latest index")
       ret = client.listunspent(addresses = ["2MxBZG7295wfsXaUj69quf8vucFzwG35UWh"])
       json_print(ret)

       print("*"*30 + "get proof base info")
       ret = client.violas_listexproof(0, 11)
       json_print(ret)
    except Exception as e:
        parse_except(e)
    finally:
        print("end main")

if __name__ == "__main__":
    main()
