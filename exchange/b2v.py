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
from btc.btcclient import btcclient
import violas.violasclient
from violas.violasclient import violasclient, violaswallet
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
#from .models import BtcRpc
from enum import Enum

#module name
name="exchangeb2v"

COINS = 1000000000
#load logging
logger = log.logger.getLogger(name) 

    
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

def grant_vbtc(vclient, from_account, to_address, amount, module_address):
    try:
        ret = vclient.send_coins(from_account, to_address, amount, module_address)
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

        ret = result(error.SUCCEED, "", rpcparams)
    except Exception as e:
        logger.error(traceback.format_exc(setting.traceback_limit))
        ret = result(error.EXCEPT, e, "")
    return ret
def checks():
    assert (len(setting.btc_conn) == 4), "btc_conn is invalid."
    assert (len(setting.violas_recever) == 64 ), "violas_recever is invalid."
    assert (len(setting.violas_sender) == 64 ), "violas_sender is invalid."
    assert (len(setting.module_address) == 64), "module_address is invalid"
    assert (len(setting.violas_nodes) > 0 and len(setting.violas_nodes[0]) > 1), "violas_nodes is invalid."

def works():

    try:
        logger.debug("start works")
        dbb2v_name = "bve_b2v.db"
        dbv2b_name = "bve_v2b.db"
        wallet_name = "vwallet"

        #requirement checks
        checks()

        #btc init
        exg = btcclient(setting.traceback_limit, setting.btc_conn)
        b2v = dbb2v(dbb2v_name, setting.traceback_limit)

        #violas init
        vclient = violasclient(setting.traceback_limit, setting.violas_nodes)
        vwallet = violaswallet(setting.traceback_limit, wallet_name)
        ret = vwallet.get_account(setting.violas_sender)
        if ret.state != error.SUCCEED:
            return result(error.FAILED, "not fount violas sender account({}".format(setting.violas_sender)) 

        #violas sender, grant vbtc
        vsender = ret.datas
        module_address = setting.module_address
         
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
                    ##check 
                    to_address = data["address"]
                    to_module_address = data["vtoken"]
                    vamount = int(float(data["amount"]) * COINS)
                    if (len(module_address) != 64 or module_address != to_module_address):
                       logger.warning("vtoken({}) is invalid.".format(to_module_address))
                       continue
                    if vamount <= 0:
                        logger.warning("amount({}) is invalid.".format(vamount))
                        continue

                    ##create new row to db. state = start 
                    ret = b2v.insert_b2vinfo_commit(data["txid"], data["issuer"], data["receiver"], int(float(data["amount"] * COINS)), 
                            data["address"], int(data["sequence"]), 0, data["vtoken"], data["creation_block"], data["update_block"])
                    assert (ret.state == error.SUCCEED), "insert_b2vinfo_commit error"


                    ##send vbtc to vaddress, vtoken and amount
                    ret = vclient.send_coins(vsender, to_address, vamount, to_module_address)

                    rettmp = client.get_address_sequence(vsender.address.hex())
                    height = -1
                    if rettmp.state == error.SUCCEED:
                        height = ret.datas

                    ##update db 
                    ###failed: dbb2v state = failed
                    ###succeed:dbb2v state = succeed
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

def main():
       logger.debug("start main")
       ret = works()
       if ret.state != error.SUCCEED:
           logger.error(ret.message)

if __name__ == "__main__":
    main()
