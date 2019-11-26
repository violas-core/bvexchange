#!/usr/bin/python3
import operator
import sys
import json
sys.path.append("..")
import libra
from libra import Client
from libra import WalletLibrary
from libra.json_print import json_print
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
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
#from .models import BtcRpc
from enum import Enum

#module name
name="exchangeb2v"

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
        exg = btcclient(setting.traceback_limit, setting.btc_conn)
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

def test_libra():
    wallet = WalletLibrary.new()
    a1 = wallet.new_account()
    a2 = wallet.new_account()
    client = Client.new('18.220.66.235',40001, "./violas_config/consensus_peers.config.toml", "./violas_config/temp_faucet_keys")
    client.mint_coins(a1.address, 100, True)
    client.mint_coins(a2.address, 100, True)

    client.violas_publish(a1, True)
    client.violas_init(a1, a1.address, True)
    client.violas_init(a2, a1.address, True)
    client.violas_mint_coin(a1.address, 100, a1, True)
    print("before............")
    print("libra balance:", "a1=", client.get_balance(a1.address), "a2=", client.get_balance(a2.address))
    print("violas balance:", "a1=", client.violas_get_balance(a1.address, a1.address), "a2=", client.violas_get_balance(a2.address, a1.address))

    print("before:", client.violas_get_balance(a1.address, a1.address), client.violas_get_balance(a2.address, a1.address))
    client.violas_transfer_coin(a1, a2.address, 20, a1.address, is_blocking=True)
    print("after:", client.violas_get_balance(a1.address, a1.address), client.violas_get_balance(a2.address, a1.address))
def main():
    try:
       logger.debug("start main")
       #ret = works()
       #if ret.state != error.SUCCEED:
       #    logger.error(ret.message)
       test_libra()
    except Exception as e:
        logger.error(traceback.format_exc(setting.traceback_limit))
    finally:
        logger.info("end main")

if __name__ == "__main__":
    #main()
    test_libra()
