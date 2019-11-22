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

    def __del__(self):
        logger.debug("start __del__")

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
            logger.error(traceback.format_exc(self.__traceback_limit))
            ret = result(error.EXCEPT, e, "")
        return ret

    def isexproofcomplete(self, address, sequence):
        try:
            logger.debug("start isexproofcomplete (address = %s sequence=%i)"%(address, sequence))
            if(len(address) != 64 or sequence < 0):
                return result(error.ARG_INVALID, error.argument_invalid, "")
                
            datas = self.__rpc_connection.violas_isexproofcomplete(address, sequence)
            return result(error.SUCCEED, "", datas)

        except Exception as e:
            logger.error(traceback.format_exc(self.__traceback_limit))
            ret = result(error.EXCEPT, "", "")
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
            return result(error.SUCCEED, "", datas)
        except Exception as e:
            logger.error(traceback.format_exc(self.__traceback_limit))
            ret = result(error.EXCEPT, "", "")
        return ret
    
def merge_proof_to_rpcparams(rpcparams, dbinfos):
    try:
        logger.debug("start merge_proof_to_rpcparams")
        for info in dbinfos:
            if info.toaddress in rpcparams:
                rpcparams[info.toaddress].append({"address":"%s"%(info.vaddress), "sequence":info.sequence})
            else:
                rpcparams[info.toaddress] = [{"address":"%s"%(info.vaddress), "sequence":info.sequence}]

        return result(error.SUCCEED, "", rpcparams)
    except Exception as e:
        logger.error(traceback.format_exc(setting.traceback_limit))
        ret = result(error.EXCEPT, e, "")
    return ret

def grant_vtoken(btcinfo):
    try:
        return result(error.SUCCEED, "", "") 
    except Exception as e:
        logger.error(traceback.format_exc(setting.traceback_limit))
        ret = result(error.EXCEPT, e, "")
    return ret

def get_excluded(b2v):
    try:
        rpcparams = {}
        #Proof that integration should be excluded(dbb2v.db)
        ## succeed
        scddatas = b2v.query_b2vinfo_is_succeed()
        if(scddatas.state != error.SUCCEED):
            return scddatas

        ret = merge_proof_to_rpcparams(rpcparams, scddatas.datas)
        if(ret.state != error.SUCCEED):
            return ret

        ## start 
        stdatas = b2v.query_b2vinfo_is_start()
        if(stdatas.state != error.SUCCEED):
            return sddatas

        ret = merge_proof_to_rpcparams(rpcparams, stdatas.datas)
        if(ret.state != error.SUCCEED):
            return ret

        ## failed 
        flddatas = b2v.query_b2vinfo_is_failed()
        if(flddatas.state != error.SUCCEED):
            return flddatas

        ret = merge_proof_to_rpcparams(rpcparams, flddatas.datas)
        if(ret.state != error.SUCCEED):
            return ret

        ## btcfailed 
        bflddatas = b2v.query_b2vinfo_is_btcfailed()
        if(bflddatas.state != error.SUCCEED):
            return bflddatas

        ret = merge_proof_to_rpcparams(rpcparams, bflddatas.datas)
        if(ret.state != error.SUCCEED):
            return ret

        del scddatas
        del stdatas
        del flddatas
        del bflddatas

    except Exception as e:
        logger.error(traceback.format_exc(setting.traceback_limit))
        ret = result(error.EXCEPT, e, "")
    return ret

def works():

    try:
        logger.debug("start works")
        #btc rpc 
        exg = exchange(setting.traceback_limit, setting.btc_conn)
        b2v = dbb2v("bve_b2v.db", setting.traceback_limit)
        combineaddress = setting.combineaddress

        #update db state by proof state
        ##search db state is succeed
        scddatas = b2v.query_b2vinfo_is_succeed()
        if(scddatas.state != error.SUCCEED):
            return scddatas

        ##excluded btc blockchain state is not start,update dbb2v state to complete
        ##dbb2v state is complete, that means  btc blockchain state is cancel or succeed
        for row in scddatas.datas:
            vaddress  = row.vaddress
            sequence = row.sequence
            ret = exg.isexproofcomplete(vaddress, sequence)
            if(ret.state == error.SUCCEED and ret.datas["result"] == "true"):
                b2v.update_b2vinfo_to_complete_commit(vaddress, sequence)
        del scddatas

        #get all excluded info from db
        rpcparams = {}
        ret = get_excluded(b2v)
        if(ret.state != error.SUCCEED):
            return ret
        rpcparams = ret.datas

        #set receiver: get it from setting or get it from blockchain
        receivers = list(set(setting.receivers))
        logger.debug(receivers)

        #modulti receiver, one-by-one
        for receiver in receivers:
            excluded = []
            if receiver in rpcparams:
                excluded = rpcparams[receiver]

            logger.debug("check receiver=%s excluded=%s"%(receiver, excluded))
            ret = exg.listexproofforstart(receiver, excluded)
            if ret.state == error.SUCCEED and len(ret.datas) > 0:
                for data in ret.datas:
                    #grant vbtc 
                    ##create new row to db. state = start 
                    ret = b2v.insert_b2vinfo_commit(data["txid"], data["issuer"], data["receiver"], int(data["amount"]), 
                            data["address"], int(data["sequence"]), 0, data["vtoken"], data["creation_block"], data["update_block"])

                    if(ret.state != error.SUCCEED):
                        return ret

                    ##send vbtc to vaddress, vtoken and amount
                    ret = grant_vtoken(data)
                    height = 10 #from grant_vtoken ret import
                    vamount = int(data["amount"]) # from grant_vtoken import

                    ##failed: dbb2v state = failed
                    ##succeed:dbb2v state = succeed
                    if ret.state != error.SUCCEED:
                        logger.debug("grant_vtoken error")
                        ret = b2v.update_b2vinfo_to_failed_commit(data["address"], int(data["sequence"]))
                    else:
                        ret = exg.sendexproofend(receiver, combineaddress, data["address"], int(data["sequence"]), str(vamount), height)
                        if ret.state != error.SUCCEED:
                            b2v.update_b2vinfo_to_btcfailed_commit(data["address"], int(data["sequence"]))
                            continue

                        ret =b2v.update_b2vinfo_to_succeed_commit(data["address"], int(data["sequence"]), height)
                        if(ret.state != error.SUCCEED):
                            return ret

        ret = result(error.SUCCEED, "", "") 

    except Exception as e:
        logger.error(traceback.format_exc(setting.traceback_limit))
        ret = result(error.EXCEPT, "", "") 
    finally:
        logger.info("works end.")

    return ret


exg = exchange(setting.traceback_limit, setting.btc_conn)
def test_conn():
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
       #test_conn()
       ret = works()
       if ret.state != error.SUCCEED:
           logger.error(ret.message)
    except Exception as e:
        logger.error(traceback.format_exc(setting.traceback_limit))
    finally:
        logger.info("end main")

if __name__ == "__main__":
    main()
