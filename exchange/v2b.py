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
from db.dbv2b import dbv2b
from btc.btcclient import btcclient
import violas.violasclient
from violas.violasclient import violasclient, violaswallet, violasserver
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
#from .models import BtcRpc
from enum import Enum

#module name
name="exchangev2b"

COINS = comm.values.COINS
#load logging
logger = log.logger.getLogger(name) 
    
def merge_v2b_to_rpcparams(rpcparams, dbinfos):
    try:
        logger.debug("start merge_v2b_to_rpcparams")
        for info in dbinfos:
            if info.toaddress in rpcparams:
                rpcparams[info.toaddress].append({"address":"%s"%(info.vaddress), "sequence":info.sequence, "module":info.vtoken, "version":info.version})
            else:
                rpcparams[info.toaddress] = [{"address":"%s"%(info.vaddress), "sequence":info.sequence, "module":info.vtoken, "version":info.version}]

        return result(error.SUCCEED, "", rpcparams)
    except Exception as e:
        logger.debug(traceback.format_exc(setting.traceback_limit))
        logger.error(str(e))
        ret = result(error.EXCEPT, str(e), e)
    return ret

def get_reexchange(v2b):
    try:
        rpcparams = {}
        #transactions that should be get_reexchange(dbv2b.db)
        
        ## btcfailed 
        bflddatas = v2b.query_v2binfo_is_failed()
        if(bflddatas.state != error.SUCCEED):
            return bflddatas

        ret = merge_v2b_to_rpcparams(rpcparams, bflddatas.datas)
        if(ret.state != error.SUCCEED):
            return ret
        
        ret = result(error.SUCCEED, "", rpcparams)
    except Exception as e:
        logger.debug(traceback.format_exc(setting.traceback_limit))
        logger.error(str(e))
        ret = result(error.EXCEPT, str(e), e)
    return ret
def checks():
    assert (len(setting.btc_conn) == 4), "btc_conn is invalid."
    assert (len(setting.sender) > 20), "sender is invalid"
    assert (len(setting.module_address) == 64), "module_address is invalid"
    assert (len(setting.violas_servers) > 0 and len(setting.violas_servers[0]) > 1), "violas_nodes is invalid."
    assert (len(setting.violas_receivers) > 0), "violas_server is invalid."
    for violas_receiver in setting.violas_receivers:
        assert len(violas_receiver) == 64, "violas receiver({}) is invalid".format(violas_receiver)

def hasbtcbanlance(btcclient, address, vamount, gas = 1000):
    try:
        ret = btcclient.getwalletaddressbalance(address)
        if ret.state != error.SUCCEED:
            return ret

        #change bitcoin unit to satoshi and check amount is sufficient
        wbalance = int(ret.datas * COINS)
        if wbalance <= (vamount + gas): #need some gas, so wbalance > vamount
            ret = result(error.SUCCEED, "", False)
        else:
            ret = result(error.SUCCEED, "", True)
    except Exception as e:
        logger.debug(traceback.format_exc(setting.traceback_limit))
        logger.error(str(e))
        ret = result(error.EXCEPT, str(e), e)
    return ret
def works():

    try:
        logger.debug("start works")
        dbv2b_name = "bve_v2b.db"
        wallet_name = "vwallet"

        #requirement checks
        checks()

        #btc init
        exg = btcclient(setting.traceback_limit, setting.btc_conn)
        v2b = dbv2b(dbv2b_name, setting.traceback_limit)

        #violas init
        vserver = violasserver(setting.traceback_limit, setting.violas_servers)

        module_address = setting.module_address
         
        combineaddress = setting.combineaddress

        #reexchange (db's state is failed)
        flddatas = v2b.query_v2binfo_is_failed()
        if(flddatas.state != error.SUCCEED):
            return flddatas

        ##re exchange, tmp ignore


        #get all excluded info from db
        rpcparams = {}
        ret = get_reexchange(v2b)
        if(ret.state != error.SUCCEED):
            return ret
        rpcparams = ret.datas

        #set receiver: get it from setting or get it from blockchain
        sender = setting.sender
        logger.debug(sender)

        receivers = list(set(setting.violas_receivers))
        #modulti receiver, one-by-one
        for receiver in receivers:
            ret = v2b.query_latest_version(receiver, module_address)
            assert ret.state == error.SUCCEED, "get latest version error"
            latest_version = ret.datas + 1
            max_version = 0

            logger.debug("start exchange v2b. receiver = {}, latest version = {}".format(receiver, latest_version - 1))

            #get old transaction from db, check transaction. version and receiver is current value
            failed = None#rpcparams.get(receiver)
            if failed is not None:
                logger.debug("start exchange failed datas from db. receiver={}".format(receiver))

                for data in failed:
                    vaddress = data.vaddress
                    vamount = data.vamount
                    fmtamount = data.vamount / COINS
                    sequence = data.sequence
                    version = data.version
                    baddress = data.toaddress
                    module_old = data.vtoken

                    #check version, get transaction list is ordered?
                    #if version >= (latest_version - 1):
                    #    continue

                    #not found , process next
                    ret = vserver.has_transaction(vaddress, module_old, baddress, sequence, vamount, version)
                    if ret.state != error.SUCCEED:
                        continue

                    #check btc amount
                    gas = 1000
                    ret = hasbtcbanlance(exg, sender, vamount, gas)
                    if ret.state != error.SUCCEED or ret.datas != True:
                        continue
                    if ret.datas != True:
                        logger.info("{} not enough btc coins(vamount = {}, gas ={})". format(sender, fmtamount, float(gas)/COINS))
                        continue

                    #send btc and mark it in OP_RETURN
                    ret = exg.sendbtcproofmark(sender, baddress, str(fmtamount), vaddress, sequence, str(fmtamount), str(sequence))
                    txid = ret.datas
                    #update db state
                    if ret.state == error.SUCCEED:
                        ret = v2b.update_v2binfo_to_succeed_commit(vaddress, sequence, txid)
                        assert (ret.state == error.SUCCEED), "db error"

            #get new transaction from violas server
            ret = vserver.get_transactions(receiver, module_address, latest_version)
            if ret.state == error.SUCCEED and len(ret.datas) > 0:
                logger.debug("start exchange datas from violas server. receiver={}".format(receiver))
                for data in ret.datas:
                    #grant vbtc 
                    ##check 
                    vaddress = data["address"]
                    vamount = int(data["amount"]) 
                    fmtamount = float(vamount) / COINS
                    sequence = data["sequence"] 
                    version = data["version"]
                    baddress = data["baddress"]

                    max_version = max(version, max_version)
                    ret = v2b.has_v2binfo(vaddress, sequence)
                    assert ret.state == error.SUCCEED, "has_v2binfo(vaddress={}, sequence={}) failed.".format(vaddress, sequence)
                    if ret.datas == True:
                        logger.error("found transaction(vaddress={}, sequence={}) in db. ignore it and process next.".format(vaddress, sequence))
                        continue

                    #check btc amount
                    gas = 1000
                    ret = hasbtcbanlance(exg, sender, vamount, gas)
                    if ret.state != error.SUCCEED:
                        continue

                    if ret.datas != True:
                        logger.info("{} not enough btc coins(vamount = {}, gas ={})". format(sender,  fmtamount, float(gas)/COINS))
                        continue

                    ##send btc transaction and mark to OP_RETURN
                    ret = exg.sendbtcproofmark(sender, baddress, str(fmtamount), vaddress, sequence, str(fmtamount), str(sequence))
                    txid = ret.datas
                    logger.debug(txid)
                    #save db amount is satoshi, so db value's violas's amount == btc's amount 
                    if ret.state != error.SUCCEED:
                        ret = v2b.insert_v2binfo_commit("", sender, baddress, vamount, vaddress, sequence, vamount, module_address, version, dbv2b.state.FAILED)
                        assert (ret.state == error.SUCCEED), "db error"
                    else:
                        ret = v2b.update_or_insert_version_commit(receiver, module_address, max_version)
                        assert (ret.state == error.SUCCEED), "db error"

                        ret = v2b.insert_v2binfo_commit(txid, sender, baddress, vamount, vaddress, sequence, vamount, module_address, version, dbv2b.state.SUCCEED)
                        assert (ret.state == error.SUCCEED), "db error"

        ret = result(error.SUCCEED) 

    except Exception as e:
        logger.debug(traceback.format_exc(setting.traceback_limit))
        logger.error(str(e))
        ret = result(error.EXCEPT, str(e), e) 
    finally:
        logger.info("works end.")

    return ret

def main():
       logger.debug("start main")
       ret = works()
       if ret.state != error.SUCCEED:
           logger.error(ret.message)

if __name__ == "__main__":
    main()
