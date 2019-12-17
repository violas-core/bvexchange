#!/usr/bin/python3
import operator
import sys, os
import json
sys.path.append(os.getcwd())
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
            new_data = {"vaddress":info.vaddress, "sequence":info.sequence, "vtoken":info.vtoken,\
                    "version":info.version, "baddress":info.toaddress, "vreceiver":info.vreceiver, \
                    "vamount":info.vamount, "times":info.times}
            if info.vreceiver in rpcparams.keys():
                rpcparams[info.vreceiver].append(new_data)
            else:
                rpcparams[info.vreceiver] = [new_data]

        return result(error.SUCCEED, "", rpcparams)
    except Exception as e:
        logger.debug(traceback.format_exc(setting.traceback_limit))
        logger.error(str(e))
        ret = result(error.EXCEPT, str(e), e)
    return ret

def get_reexchange(v2b):
    try:
        maxtimes = 5
        rpcparams = {}
        #transactions that should be get_reexchange(dbv2b.db)
        
        ## btcfailed 
        if setting.v2b_maxtimes and setting.v2b_maxtimes > 0:
            maxtimes = setting.v2b_maxtimes
        bflddatas = v2b.query_v2binfo_is_failed(maxtimes)
        if(bflddatas.state != error.SUCCEED):
            return bflddatas
        logger.debug("get count = {}".format(len(bflddatas.datas)))

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
    assert (len(setting.btc_senders) > 0), "btc_senders is invalid"
    assert (len(setting.module_address) == 64), "module_address is invalid"
    assert (len(setting.violas_servers) > 0 and len(setting.violas_servers[0]) > 1), "violas_nodes is invalid."
    assert (len(setting.violas_receivers) > 0), "violas_server is invalid."
    for violas_receiver in setting.violas_receivers:
        assert len(violas_receiver) == 64, "violas receiver({}) is invalid".format(violas_receiver)

    for sender in setting.btc_senders:
        assert len(sender) >= 20, "btc address({}) is invalied".format(sender)

def get_btc_sender_address(bclient, excludeds, amount, gas):
    try:
        use_sender = None
        for sender in setting.btc_senders:
            if sender not in excludeds:
               #check btc amount
               ret = bclient.has_btc_banlance(sender, amount, gas)
               if ret.state != error.SUCCEED or ret.datas != True:
                   continue
               if ret.datas != True:
                   continue
               use_sender = sender
               break;

        if use_sender is not None:
            ret = result(error.SUCCEED, "", use_sender)
        else:
            ret = result(error.FAILED)
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
        bclient = btcclient(setting.traceback_limit, setting.btc_conn)
        v2b = dbv2b(dbv2b_name, setting.traceback_limit)

        #violas init
        vserver = violasserver(setting.traceback_limit, setting.violas_servers)

        module_address = setting.module_address

        gas = 1000
        
        #get all excluded info from db
        rpcparams = {}
        ret = get_reexchange(v2b)
        if(ret.state != error.SUCCEED):
            return ret
        rpcparams = ret.datas

        receivers = list(set(setting.violas_receivers))
        #modulti receiver, one-by-one
        for receiver in receivers:
            ret = v2b.query_latest_version(receiver, module_address)
            assert ret.state == error.SUCCEED, "get latest version error"
            latest_version = ret.datas + 1
            max_version = 0

            #get old transaction from db, check transaction. version and receiver is current value
            failed = rpcparams.get(receiver)
            if failed is not None:
                logger.debug("start exchange failed datas from db. receiver={}".format(receiver))
                for data in failed:
                    vaddress = data["vaddress"]
                    vamount = data["vamount"]
                    fmtamount = float(vamount) / COINS
                    sequence = int(data["sequence"])
                    version = int(data["version"])
                    baddress = data["baddress"]
                    module_old = data["vtoken"]
                    vreceiver = data["vreceiver"]
                    times    = data["times"]

                    logger.debug(f"start exchange v2b(times={times}), datas from db. receiver = {receiver}, vaddress={vaddress} sequence={sequence} baddress={baddress} {fmtamount: .8f}") 

                    #check version, get transaction list is ordered ?
                    #if version >= (latest_version - 1):
                    #    continue

                    #match module 
                    if module_old != module_address:
                        logger.debug("module is not match.")
                        ret = v2b.update_v2binfo_to_failed_commit(vaddress, sequence, version)
                        assert (ret.state == error.SUCCEED), "db error"
                        continue

                    #not found , process next
                    ret = vserver.has_transaction(vaddress, module_old, baddress, sequence, vamount, version, vreceiver)
                    if ret.state != error.SUCCEED or ret.datas != True:
                        logger.debug("not found transaction from violas server.")
                        ret = v2b.update_v2binfo_to_failed_commit(vaddress, sequence, version)
                        assert (ret.state == error.SUCCEED), "db error"
                        continue

                    #get btc sender from setting.btc_senders
                    ret = get_btc_sender_address(bclient, [baddress], vamount, gas) #vamount and gas unit is satoshi
                    if ret.state != error.SUCCEED:
                        logger.debug("not found btc sender. check btc address and amount")
                        continue
                    sender = ret.datas

                    #send btc and mark it in OP_RETURN
                    ret = bclient.sendexproofmark(sender, baddress, fmtamount, vaddress, sequence, version)
                    txid = ret.datas
                    logger.debug(f"txid={txid}")
                    #update db state
                    if ret.state == error.SUCCEED:
                        max_version = max(version, max_version)
                        ret = v2b.update_or_insert_version_commit(receiver, module_address, max_version)
                        assert (ret.state == error.SUCCEED), "db error"

                        ret = v2b.update_v2binfo_to_succeed_commit(vaddress, sequence, version, txid)
                        assert (ret.state == error.SUCCEED), "db error"
                    else:
                        ret = v2b.update_v2binfo_to_failed_commit(vaddress, sequence, version)
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

                    logger.debug("start exchange v2b. receiver = {}, vaddress={} sequence={} baddress={} amount={} \
                            datas from server.".format(receiver, vaddress, sequence, baddress, fmtamount))

                    max_version = max(version, max_version)

                    #if found transaction in v2b.db, then get_transactions's latest_version is error(too small or other case)'
                    ret = v2b.has_v2binfo(vaddress, sequence, version)
                    assert ret.state == error.SUCCEED, "has_v2binfo(vaddress={}, sequence={}) failed.".format(vaddress, sequence)
                    if ret.datas == True:
                        logger.info("found transaction(vaddress={}, sequence={}) in db. ignore it and process next.".format(vaddress, sequence))
                        continue

                    #get btc sender from setting.btc_senders
                    ret = get_btc_sender_address(bclient, [baddress], fmtamount, gas)
                    if ret.state != error.SUCCEED:
                        logger.debug("not found btc sender or amount too low. check btc address and amount")
                        ret = v2b.insert_v2binfo_commit("", sender, baddress, vamount, vaddress, sequence, vamount, module_address, version, dbv2b.state.FAILED)
                        assert (ret.state == error.SUCCEED), "db error"
                        continue
                    sender = ret.datas

                    ##send btc transaction and mark to OP_RETURN
                    ret = bclient.sendexproofmark(sender, baddress, fmtamount, vaddress, sequence, version)
                    txid = ret.datas
                    logger.debug(f"txid={txid}")
                    #save db amount is satoshi, so db value's violas's amount == btc's amount 
                    if ret.state != error.SUCCEED:
                        ret = v2b.insert_v2binfo_commit("", sender, baddress, vamount, vaddress, sequence, version, vamount, module_address, receiver, dbv2b.state.FAILED)
                        assert (ret.state == error.SUCCEED), "db error"
                    else:
                        ret = v2b.update_or_insert_version_commit(receiver, module_address, max_version)
                        assert (ret.state == error.SUCCEED), "db error"

                        ret = v2b.insert_v2binfo_commit(txid, sender, baddress, vamount, vaddress, sequence, version, vamount, module_address, receiver, dbv2b.state.SUCCEED)
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
