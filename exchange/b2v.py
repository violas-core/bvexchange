#!/usr/bin/python3
import operator
import sys, os
import json
import log
sys.path.append(os.getcwd())
import log.logger
import traceback
import datetime
import sqlalchemy
import stmanage
import requests
import comm
import comm.error
import comm.result
import comm.values
from comm.result import result, parse_except
from comm.error import error
from db.dbb2v import dbb2v
from btc.btcclient import btcclient
import violas.violasclient
from violas.violasclient import violasclient, violaswallet
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
#from .models import BtcRpc
from enum import Enum

#module name
name="b2v"
btc_chain = "btc"
violas_chain = "violas"

COINS = comm.values.COINS
#load logging
logger = log.logger.getLogger(name) 

    
def merge_proof_to_rpcparams(rpcparams, dbinfos):
    try:
        logger.debug("start merge_proof_to_rpcparams")
        for info in dbinfos:
            if info.toaddress in rpcparams.keys():
                rpcparams[info.toaddress].append({"address":"%s"%(info.vaddress), "sequence":info.sequence})
            else:
                rpcparams[info.toaddress] = [{"address":"%s"%(info.vaddress), "sequence":info.sequence}]

        return result(error.SUCCEED, "", rpcparams)
    except Exception as e:
        ret = parse_except(e)
    return ret

def get_excluded(b2v):
    try:
        rpcparams = {}
        #Proof that integration should be excluded(dbb2v.db)
        ## succeed
        scddatas = b2v.query_b2vinfo_is_succeed()
        if(scddatas.state != error.SUCCEED):
            return scddatas
        logger.debug("get count = {}".format(len(scddatas.datas)))

        ret = merge_proof_to_rpcparams(rpcparams, scddatas.datas)
        if(ret.state != error.SUCCEED):
            return ret
        
        ## btcfailed 
        bflddatas = b2v.query_b2vinfo_is_btcfailed()
        if(bflddatas.state != error.SUCCEED):
            return bflddatas
        logger.debug("get count = {}".format(len(bflddatas.datas)))

        ret = merge_proof_to_rpcparams(rpcparams, bflddatas.datas)
        if(ret.state != error.SUCCEED):
            return ret

        ## btcsucceed
        btcscddatas = b2v.query_b2vinfo_is_btcsucceed()
        if(btcscddatas.state != error.SUCCEED):
            return bflddatas
        logger.debug("get count = {}".format(len(btcscddatas.datas)))

        ret = merge_proof_to_rpcparams(rpcparams, btcscddatas.datas)
        if(ret.state != error.SUCCEED):
            return ret

        ret = result(error.SUCCEED, "", rpcparams)
    except Exception as e:
        ret = parse_except(e)
    return ret

def checks():
    assert (len(stmanage.get_btc_conn()) == 4), "btc_conn is invalid."
    assert (len(stmanage.get_sender_address_list(name, violas_chain)) > 0 ), "violas sender not found."
    assert (len(stmanage.get_receiver_address_list(name, btc_chain)) > 0 ), "btc receiver not found."
    assert (len(stmanage.get_module_address(name, violas_chain)) == 64), "module_address is invalid"
    assert (len(stmanage.get_violas_nodes()) > 0), "violas_nodes is invalid."
    for addr in stmanage.get_sender_address_list(name, violas_chain):
        assert len(addr) == 64, f"violas address({addr}) is invalid."

    for addr in stmanage.get_receiver_address_list(name, btc_chain):
        assert len(addr) >= 20, f"btc address({addr}) is invalid."

def hasplatformbalance(vclient, address, vamount = 0):
    try:
        ret = vclient.get_platform_balance(address)
        if ret.state != error.SUCCEED:
            return ret

        balance = ret.datas
        if balance >= vamount:
            ret = result(error.SUCCEED, "", True)
        else:
            ret = result(error.SUCCEED, "", False)
    except Exception as e:
        ret = parse_except(e)
    return ret

def hasviolasbalance(vclient, address, module, vamount):
    try:
        ret = vclient.get_violas_balance(address, module)
        if ret.state != error.SUCCEED:
            return ret

        balance = ret.datas
        if balance >= vamount:
            ret = result(error.SUCCEED, "", True)
        else:
            ret = result(error.SUCCEED, "", False)
    except Exception as e:
        ret = parse_except(e)
    return ret

def update_db_btcsucceed_to_complete(bclient, b2v):
    ##search db state is succeed
    try:
        scddatas = b2v.query_b2vinfo_is_btcsucceed()
        if scddatas.state != error.SUCCEED:
            logger.error("db error")
            return result(error.FAILED)

        ##excluded btc blockchain state is not start,update dbb2v state to complete
        ##dbb2v state is complete, that means  btc blockchain state is cancel or succeed
        for row in scddatas.datas:
            vaddress  = row.vaddress
            sequence = row.sequence
            ret = bclient.isexproofcomplete(vaddress, sequence)
            if(ret.state == error.SUCCEED and ret.datas["result"] == "true"):
                ret = b2v.update_b2vinfo_to_complete_commit(vaddress, sequence)

        ret = result(error.SUCCEED)
    except exception as e:
        ret = parse_except(e)
    return ret

def rechange_btcstate_to_end_from_btcfailed(bclient, b2v, combineaddress, module_address, receivers):
    try:
        logger.debug(f"start rechange_btcstate_to_end_from_btcfailed(combineaddress={combineaddress}, module_address={module_address}, receivers={receivers})")
        bflddatas = b2v.query_b2vinfo_is_btcfailed()
        if(bflddatas.state != error.SUCCEED):
            return bflddatas
        logger.debug("get count = {}".format(len(bflddatas.datas)))

        for data in bflddatas.datas:
            receiver = data.toaddress
            if module_address != data.vtoken:
                logger.info(f"db's vtoken({data.vtoken}) not match module_address({module_address}), ignore it, next")
                continue

            if receiver not in receivers:
                logger.info(f"db's fromaddress({data.fromaddress}) not match btc_recivers({receivers}), ignore it, next")
                continue

            vaddress = data.vaddress
            bamount = data.bamount  
            sequence = data.sequence
            height = data.height

            #recheck b2v state in blockchain, may be performed manually
            ret = bclient.isexproofcomplete(vaddress, sequence)
            if(ret.state == error.SUCCEED and ret.datas["result"] == "true"):
                ret = b2v.update_b2vinfo_to_complete_commit(vaddress, sequence)
                continue

            #The receiver of the start state can change the state to end
            ret = bclient.sendexproofend(receiver, combineaddress, vaddress, sequence, float(bamount)/COINS, height)
            if ret.state != error.SUCCEED:
                ret = b2v.update_b2vinfo_to_btcfailed_commit(vaddress, sequence)
                assert (ret.state == error.SUCCEED), "db error"
            else:
                ret = b2v.update_b2vinfo_to_btcsucceed_commit(vaddress, sequence)
                assert (ret.state == error.SUCCEED), "db error"
        ret = result(error.SUCCEED)
    except Exception as e:
        ret = parse_except(e)
    return ret

def get_violas_sender(vclient, vwallet, module, vamount, min_gas):
    for sender in stmanage.get_sender_address_list(name, violas_chain):
        ret = vwallet.get_account(sender)
        if ret.state != error.SUCCEED:
            continue
        asender = ret.datas

        #make sure sender address is binded module
        ret = vclient.account_has_violas_module(sender, module)
        if ret.state != error.SUCCEED:
            logger.warning("violas client error")
            continue

        if ret.datas != True:
            logger.warning("sender account {} not bind module {}".format(sender, module))
            continue

        #make sure sender address has enough platform coins
        ret = hasplatformbalance(vclient, sender, min_gas)
        if ret.state != error.SUCCEED:
            continue

        if ret.datas != True:
            logger.warning("{} not enough platform coins {}".format(sender, min_gas))
            continue

        #make sure sender address has enough violas coins
        ret = hasviolasbalance(vclient, sender, module, vamount)
        if ret.state != error.SUCCEED:
            continue

        if ret.datas != True:
            logger.info("{} not enough {} coins {}".format(vsender_address, module, vamount))
            continue
        return(error.SUCCEED, "", (asender, sender))

    return result(error.FAILED, "not found account from wallet")


def works():
    try:
        logger.debug("start b2v work")
        dbb2v_name = "bve_b2v.db"
        wallet_name = "vwallet"

        #requirement checks
        checks()

        #btc init
        bclient = btcclient(stmanage.get_btc_conn())
        b2v = dbb2v(dbb2v_name)

        #violas init
        vclient = violasclient(stmanage.get_violas_nodes())
        vwallet = violaswallet(wallet_name)

        module_address = stmanage.get_module_address(name, violas_chain)
        combineaddress = stmanage.get_combine_address(name, btc_chain)[0]

        #update db state by proof state
        ret = update_db_btcsucceed_to_complete(bclient, b2v)
        if ret.state != error.SUCCEED:
            return ret

        #update proof state to end, and update db state, prevstate is btcfailed in db. 
        #When this happens, there is not enough Bitcoin, etc.
        rechange_btcstate_to_end_from_btcfailed(bclient, b2v, combineaddress, module_address, stmanage.get_receiver_address_list(name, btc_chain))

        #get all excluded info from db
        rpcparams = {}
        ret = get_excluded(b2v)
        if ret.state != error.SUCCEED:
            logger.error("db error")
            return result(error.FAILED)

        rpcparams = ret.datas
        min_gas = comm.values.MIN_EST_GAS 

        #set receiver: get it from stmanage or get it from blockchain
        receivers = list(set(stmanage.get_receiver_address_list(name, btc_chain)))
        logger.debug(receivers)

        #modulti receiver, one-by-one
        for receiver in receivers:
            #check receiver is included in wallet
            ret = bclient.has_btc_banlance(receiver, 0)
            if ret.state != error.SUCCEED or ret.datas != True:
                logger.warning("receiver({}) has't enough satoshi ({}). ignore it's b2v, next receiver.".format(receiver, comm.values.MIN_EST_GAS))
                continue 

            excluded = []
            if receiver in rpcparams:
                excluded = rpcparams[receiver]

            logger.debug("check receiver={} excluded={}".format(receiver, excluded))
            ret = bclient.listexproofforstart(receiver, excluded)
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
                    
                    #get sender account and address
                    ret = get_violas_sender(vclient, vwallet, to_module_address, vamount, min_gas)
                    if ret.state != error.SUCCEED:
                        logger.debug(f"get violas account failed. {ret.message}")
                        continue

                    #violas sender, grant vbtc
                    vsender  = ret.datas(0)
                    vsender_address = ret.datas(1)
                                #make sure receiver address is binded module
                    ret = vclient.account_has_violas_module(to_address, to_module_address)
                    if ret.state != error.SUCCEED:
                        continue

                    if ret.datas != True:
                        logger.warning("account {} not bind module {}".format(to_address, to_module_address))
                        continue
                       
                    logger.debug("start new btc -> vbtc(address={}, sequence={} amount={}, module={})".format(to_address, int(data["sequence"]), vamount, to_module_address))
                    ##send vbtc to vaddress, vtoken and amount
                    ret = vclient.send_coin(vsender, to_address, vamount, to_module_address, data="btctxid:{}".format(data["txid"]))
                    if ret.state != error.SUCCEED:
                        continue
                    
                    ##create new row to db. state = start 
                    ret = b2v.has_b2vinfo(data["address"], data["sequence"])
                    assert (ret.state == error.SUCCEED), "db error"

                    if ret.datas == False:
                        ret = b2v.insert_b2vinfo_commit(data["txid"], data["issuer"], data["receiver"], int(float(data["amount"]) * COINS), 
                                data["address"], int(data["sequence"]), int(float(data["amount"]) * COINS), data["vtoken"], data["creation_block"], data["update_block"])
                        assert (ret.state == error.SUCCEED), "db error"

                    rettmp = vclient.get_address_sequence(vsender_address)
                    height = -1
                    ##update db 
                    ###succeed:dbb2v state = succeed
                    if rettmp.state == error.SUCCEED:
                        height =  rettmp.datas
                        ret =b2v.update_b2vinfo_to_succeed_commit(data["address"], int(data["sequence"]), height)
                        assert (ret.state == error.SUCCEED), "db error"
                    
                    #The receiver of the start state can change the state to end
                    ret = bclient.sendexproofend(receiver, combineaddress, data["address"], int(data["sequence"]), float(vamount)/COINS, height)
                    if ret.state != error.SUCCEED:
                        ret = b2v.update_b2vinfo_to_btcfailed_commit(data["address"], int(data["sequence"]))
                        assert (ret.state == error.SUCCEED), "db error"
                    else:
                        ret = b2v.update_b2vinfo_to_btcsucceed_commit(data["address"], int(data["sequence"]))
                        assert (ret.state == error.SUCCEED), "db error"

        ret = result(error.SUCCEED) 

    except Exception as e:
        ret = parse_except(e)
    finally:
        vclient.disconn_node()
        vwallet.dump_wallet()
        logger.info("works end.")

    return ret

def main():
       logger.debug("start main")
       ret = works()
       if ret.state != error.SUCCEED:
           logger.error(ret.message)

if __name__ == "__main__":
    main()
