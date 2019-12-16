#!/usr/bin/python3
import operator
import sys
import json
sys.path.append("..")
import log
import log.logger
import traceback
import datetime
import sqlalchemy
import setting
import requests
import comm
import comm.error
import comm.result
import comm.values
from comm.result import result
from comm.error import error
from db.dbb2v import dbb2v
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
#from .models import BtcRpc
from enum import Enum

#module name
name="btcclient"

#load logging
logger = log.logger.getLogger(name) 

#btc_url = "http://%s:%s@%s:%i"


class btcclient:
    __traceback_limit       = 0
    __btc_url               = "http://%s:%s@%s:%i"
    __rpcuser               = "btc"
    __rpcpassword           = "btc"
    __rpcip                 = "127.0.0.1"
    __rpcport               = 9409
    __rpc_connection        = ""

    class proofstate(Enum):
        START   = "start"
        END     = "end"
        CANCEL  = "cancel"
        MARK    = "mark"

    def __init__(self, traceback_limit, btc_conn):
        self.__traceback_limit = traceback_limit
        if btc_conn :
            if btc_conn["rpcuser"]:
                self.__rpcuser = btc_conn["rpcuser"]
            if btc_conn["rpcpassword"]:
                self.__rpcpassword = btc_conn["rpcpassword"]
            if btc_conn["rpcip"]:
                self.__rpcip = btc_conn["rpcip"]
            if btc_conn["rpcport"]:
                self.__rpcport = btc_conn["rpcport"]
        logger.info("connect btc server(rpcuser={}, rpcpassword={}, rpcip={}, rpcport={})".format(btc_conn["rpcuser"], btc_conn["rpcpassword"], btc_conn["rpcip"], btc_conn["rpcport"]))
        self.__rpc_connection = AuthServiceProxy(self.__btc_url%(self.__rpcuser, self.__rpcpassword, self.__rpcip, self.__rpcport))

    def __listexproofforstate(self, state, extype, receiver, excluded):
        try:
            logger.debug("start __listexproofforstate(state={state} type={extype} receiver={receiver} excluded={excluded})")
            if(len(receiver) == 0):
                return result(error.ARG_INVALID, error.argument_invalid, "")
            
            if excluded is None or len(excluded) == 0:
                datas = self.__rpc_connection.violas_listexproofforstate(state, extype, receiver)
            else:
                datas = self.__rpc_connection.violas_listexproofforstate(state, extype, receiver, excluded)

            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.EXCEPT, str(e), e) 
        return ret

    def isexproofcomplete(self, address, sequence):
        try:
            logger.debug("start isexproofcomplete (address = %s sequence=%i)"%(address, sequence))
            if(len(address) != 64 or sequence < 0):
                return result(error.ARG_INVALID, error.argument_invalid, "")
                
            datas = self.__rpc_connection.violas_isexproofcomplete(address, sequence)
            logger.debug(datas)
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.EXCEPT, str(e), e) 
        return ret

    def listexproofforstart(self, receiver, excluded):
        return self.__listexproofforstate(self.proofstate.START.value, comm.values.EX_TYPE_B2V, receiver, excluded)

    def listexproofforend(self, receiver, excluded):
        return self.__listexproofforstate(self.proofstate.END.value, comm.values.EX_TYPE_B2V, receiver, excluded)

    def listexproofforcancel(self, receiver, excluded):
        return self.__listexproofforstate(self.proofstate.CANCEL.value, comm.values.EX_TYPE_B2V, receiver, excluded)

    def listexproofformark(self, receiver, excluded):
        return self.__listexproofforstate(self.proofstate.MARK.value, comm.values.EX_TYPE_V2B, receiver, excluded)

    def sendexproofstart(self, fromaddress, toaddress, amount, vaddress, sequence, vtoken):
        try:
            logger.debug(f"start sendexproofstart (fromaddress={fromaddress}, toaddress={toaddress}, amount={amount:.8f}, vaddress={vaddress}, sequence={sequence}, vtoken={vtoken})")
            if(len(fromaddress) == 0 or len(toaddress) == 0 or fromaddress == toaddress or len(vaddress) != 64 \
                    or sequence < 0 or len(vtoken) != 64):
                return result(error.ARG_INVALID, "len(fromaddress) == 0 or len(toaddress) == 0 or fromaddress == toaddress or len(vaddress) != 64 or sequence < 0 or len(vtoken) !=64", "")
            datas = self.__rpc_connection.violas_sendexproofstart(fromaddress, toaddress, f"{amount:.8f}", vaddress, sequence, vtoken)
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.EXCEPT, str(e), e) 
        return ret

    def sendexproofend(self, fromaddress, toaddress, vaddress, sequence, amount, version):
        try:
            logger.debug(f"start sendexproofend (fromaddress={fromaddress}, toaddress={toaddress}, vaddress={vaddress}, sequence={sequence}, amount={amount:.8f}, version={version})")
            if(len(fromaddress) == 0 or len(toaddress) == 0 or fromaddress == toaddress or len(vaddress) != 64 
                    or sequence < 0 or version< 0):
                return result(error.ARG_INVALID, "len(fromaddress) == 0 or len(toaddress) == 0 or fromaddress == toaddress or len(vaddress) == 0 or sequence < 0 or version < 0", "")
            datas = self.__rpc_connection.violas_sendexproofend(fromaddress, toaddress, vaddress, sequence, f"{amount:.8f}", version)
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.EXCEPT, str(e), e) 
        return ret

    def sendtoaddress(self, address, amount):
        try:
            logger.debug("start sendtoaddress(address={}, amount={})".format(address, amount))
            datas = self.__rpc_connection.sendtoaddress(address, f"{amount:.8f}")
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.EXCEPT, str(e), e)
        return ret
   
    def sendexproofmark(self, fromaddress, toaddress, toamount, vaddress, sequence, version):
        try:
            logger.debug(f"start sendexproofmark(fromaddress={fromaddress}, toaddress={toaddress}, toamount={toamount:.8f}, vaddress={vaddress}, sequence={sequence}, version={version})")
            datas = self.__rpc_connection.violas_sendexproofmark(fromaddress, toaddress, f"{toamount:.8f}", vaddress, sequence, version)
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.EXCEPT, str(e), e)
        return ret

    def generatetoaddress(self, count, address):
        try:
            logger.debug("start generatetoaddress(count={}, address={})".format(count, address))
            datas = self.__rpc_connection.generatetoaddress(count, address)
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.EXCEPT, str(e), e)
        return ret

    def listunspent(self, minconf = 1, maxconf = 9999999, addresses = None, include_unsafe = True, query_options = None):
        try:
            logger.debug("start listunspent(minconf={}, maxconf={}, addresses={}, include_unsafe={}, query_options={})".format(minconf, maxconf, addresses, include_unsafe, query_options))
            #datas = self.__rpc_connection.listunspent(minconf, maxconf, addresses, include_unsafe, query_options)
            datas = self.__rpc_connection.listunspent()
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.EXCEPT, str(e), e)
        return ret

    def help(self):
        try:
            logger.debug("start help")
            datas = self.__rpc_connection.help()
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.EXCEPT, str(e), e)
        return ret

    def getwalletbalance(self):
        try:
            logger.debug("start getwalletbalance")
            walletinfo = self.__rpc_connection.getwalletinfo()
            balance = walletinfo.get("balance", 0)
            ret = result(error.SUCCEED, "", balance)
        except Exception as e:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.EXCEPT, str(e), e)
        return ret

    def getwalletaddressbalance(self, address):
        try:
            logger.debug("start getwalletaddressbalance({})".format(address))
            addresses = [address]
            datas = self.__rpc_connection.listunspent(1, 999999999, addresses)
            balance = 0
            if len(datas) == 0:
                logger.debug("not found address({})".format(address))
                return result(error.FAILED)
            for data in datas:
                balance += data.get("amount", 0)

            ret = result(error.SUCCEED, "", balance)
        except Exception as e:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.EXCEPT, str(e), e)
        return ret

    def has_btc_banlance(self, address, vamount, gas = comm.values.MIN_EST_GAS):
        try:
            logger.debug("start has_btc_banlance(address={}, vamount={}, gas={})".format(address, vamount, gas))
            ret = self.getwalletaddressbalance(address)
            if ret.state != error.SUCCEED:
                return ret
    
            #change bitcoin unit to satoshi and check amount is sufficient
            wbalance = int(ret.datas * comm.values.COINS)
            if wbalance <= (vamount + gas): #need some gas, so wbalance > vamount
                ret = result(error.SUCCEED, "", False)
            else:
                ret = result(error.SUCCEED, "", True)
        except Exception as e:
            logger.debug(traceback.format_exc(setting.traceback_limit))
            logger.error(str(e))
            ret = result(error.EXCEPT, str(e), e)
        return ret
    

def test_conn():
    exg = btcclient(setting.traceback_limit, setting.btc_conn)
    logger.debug("start test_conn")
    ret = exg.listexproofforstart(setting.receivers[0], "")
    if ret.state == error.SUCCEED and ret.datas:
        for data in ret.datas:
            logger.info(data)

    if(ret.state != error.SUCCEED):
        raise Exception(ret)

    ret = exg.listexproofforend(setting.receivers[0], "")
    if ret.state == error.SUCCEED and ret.datas:
        for data in ret.datas:
            logger.info(data)

    ret = exg.listexproofforcancel(setting.receivers[0], "")
    if ret.state == error.SUCCEED and ret.datas:
        for data in ret.datas:
            logger.info(data)

def main():
    try:
       logger.debug("start main")
       test_conn()
    except Exception as e:
        logger.error(traceback.format_exc(setting.traceback_limit))
    finally:
        logger.info("end main")

if __name__ == "__main__":
    main()
