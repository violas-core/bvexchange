#!/usr/bin/python3
import operator
import sys
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
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
#from .models import BtcRpc
from enum import Enum

#module name
name="exchangeb2v"

#load logging
logger = log.logger.getLogger(name) 

#btc_url = "http://%s:%s@%s:%i"


class exchange:
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
        CANCEL  ="cancel"

    def __init__(self, traceback_limit):
        self.__traceback_limit = traceback_limit
        btc_conn = setting.btc_conn 
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

    def __del__(self):
        logger.debug("start __del__")

    def __listexproofforstate(self, state, receiver):
        try:
            logger.debug("start listexproofforstate (state=%s receiver=%s)"%(state, receiver))
            if(len(receiver) == 0):
                return result(error.ARG_INVALID, error.argument_invalid, "")
                
            datas = self.__rpc_connection.violas_listexproofforstate(state)
            return result(error.SUCCEED, "", datas)

        except Exception as e:
            logger.error(traceback.format_exc(self.__traceback_limit))
            ret = result(error.EXCEPT, "", datas)
        return ret

    def listexproofforstart(self, receiver):
        return self.__listexproofforstate(self.proofstate.START.value, receiver)

    def listexproofforend(self, receiver):
        return self.__listexproofforstate(self.proofstate.END.value, receiver)

    def listexproofforcancel(self, receiver):
        return self.__listexproofforstate(self.proofstate.CANCEL.value, receiver)

exg = exchange(setting.traceback_limit)

def works():
    try:
        logger.debug("start works")
        ret = exg.listexproofforstart()
        if ret.state == error.SUCCEED and ret.datas:
            for data in ret.datas:
                logger.info(data)

        return result(error.SUCCEED, "", "")

    except Exception as e:
        logger.error(traceback.format_exc(self.traceback_limit))
    finally:
        logger.info("works end.")

def test_conn():
    logger.debug("start test_conn")
    ret = exg.listexproofforstart(setting.receivers[0])
    if ret.state == error.SUCCEED and ret.datas:
        for data in ret.datas:
            logger.info(data)

    if(ret.state != error.SUCCEED):
        raise Exception(ret)

    ret = exg.listexproofforstart(setting.receivers[0])
    if ret.state == error.SUCCEED and ret.datas:
        for data in ret.datas:
            logger.info(data)

    ret = exg.listexproofforcancel(setting.receivers[0])
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
