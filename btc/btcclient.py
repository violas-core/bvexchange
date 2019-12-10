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
        self.__rpc_connection = AuthServiceProxy(self.__btc_url%(self.__rpcuser, self.__rpcpassword, self.__rpcip, self.__rpcport))

    def __listexproofforstate(self, state, receiver, excluded):
        try:
            logger.debug("start __listexproofforstate (state=%s receiver=%s excluded=%s)"%(state, receiver, excluded))
            if(len(receiver) == 0):
                return result(error.ARG_INVALID, error.argument_invalid, "")
            
            if len(excluded) == 0:
                datas = self.__rpc_connection.violas_listexproofforstate(state, receiver)
            else:
                datas = self.__rpc_connection.violas_listexproofforstate(state, receiver, excluded)

            return result(error.SUCCEED, "", datas)

        except Exception as e:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(e.message)
            ret = result(error.EXCEPT, e.message, e) 
        return ret

    def isexproofcomplete(self, address, sequence):
        try:
            logger.debug("start isexproofcomplete (address = %s sequence=%i)"%(address, sequence))
            if(len(address) != 64 or sequence < 0):
                return result(error.ARG_INVALID, error.argument_invalid, "")
                
            datas = self.__rpc_connection.violas_isexproofcomplete(address, sequence)
            ret = result(error.SUCCEED, "", datas)

        except Exception as e:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(e.message)
            ret = result(error.EXCEPT, e.message, e) 
        return ret

    def listexproofforstart(self, receiver, excluded):
        return self.__listexproofforstate(self.proofstate.START.value, receiver, excluded)

    def listexproofforend(self, receiver, excluded):
        return self.__listexproofforstate(self.proofstate.END.value, receiver, excluded)

    def listexproofforcancel(self, receiver, excluded):
        return self.__listexproofforstate(self.proofstate.CANCEL.value, receiver, excluded)

    def sendexproofend(self, fromaddress, toaddress, vaddress, sequence, amount, height):
        try:
            logger.debug("start sendexproofend (fromaddress, toaddress, vaddress, sequence, amount, height),(%s,%s,%s,%i,%s,%i)"%(fromaddress, toaddress, vaddress, sequence, amount, height))
            if(len(fromaddress) == 0 or len(toaddress) == 0 or fromaddress == toaddress or len(vaddress) == 0 
                    or sequence < 0 or height < 0):
                return result(error.ARG_INVALID, "len(fromaddress) == 0 or len(toaddress) == 0 or fromaddress == toaddress or len(vaddress) == 0 or sequence < 0 or height < 0", "")
            datas = self.__rpc_connection.violas_sendexproofend(fromaddress, toaddress, vaddress, sequence, amount, height)
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(e.message)
            ret = result(error.EXCEPT, e.message, e) 
        return ret

    def sendtoaddress(self, address, amount):
        try:
            logger.debug("start sendtoaddress(address={}, amount={})".format(address, amount))
            datas = self.__rpc_connection.sendtoaddress(address, amount)
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.EXCEPT, str(e), e)
        return ret
   
    def sendbtcproofmark(self, fromaddress, toaddress, toamount, vaddress, sequence, amount, name):
        try:
            logger.debug("start sendbtcproofmark(fromaddress={}, toaddress={}, toamount={}, vaddress={}, sequence={}, amount={}, name={})".format(
                fromaddress, toaddress, toamount, vaddress, sequence, amount, name))
            datas = self.__rpc_connection.violas_sendbtcproofmark(fromaddress, toaddress, toamount, vaddress, sequence, amount, name)
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
