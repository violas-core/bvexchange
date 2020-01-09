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
import sqlalchemy
import stmanage
import requests
import comm
import comm.error
import comm.result
import comm.values
from comm.result import result, parse_except
from comm.error import error
from db.dbv2b import dbv2b
from btc.btcclient import btcclient
import violas.violasclient
from violas.violasclient import violasclient, violaswallet, violasserver
from violas.violasproof import violasproof
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from baseobject import baseobject
from enum import Enum
from vrequest.request_client import requestclient

#module self.name
name="v2b"
wallet_name = "vwallet"

COINS = comm.values.COINS
#load logging
class exv2b(baseobject):    
    def __init__(self, name, vnodes , bnode, proofdb, module, chain = "violas"):
        baseobject.__init__(self, name)
        self.set_proof_chain(chain)
        self._vclient = violasproof(self.name(), vnodes)
        #btc init
        self._bclient = btcclient(self.name(), bnode)
        self._v2b = dbv2b(self.name(), f"{self.proof_chain()}_{self.name()}.db")
    
        #violas init
        #vserver = violasserver(self.name(), stmanage.get_violas_servers())
        self._vserver = requestclient(self.name(), proofdb)
        self._module_address = module

    def __merge_v2b_to_rpcparams(self, rpcparams, dbinfos):
        try:
            self._logger.debug("start __merge_v2b_to_rpcparams")
            for info in dbinfos:
                new_data = {"vaddress":info.vaddress, "sequence":info.sequence, "vtoken":info.vtoken,\
                        "version":info.version, "baddress":info.toaddress, "vreceiver":info.vreceiver, \
                        "vamount":info.vamount, "times":info.times, "tran_id":info.tranid}
                if info.vreceiver in rpcparams.keys():
                    rpcparams[info.vreceiver].append(new_data)
                else:
                    rpcparams[info.vreceiver] = [new_data]
    
            return result(error.SUCCEED, "", rpcparams)
        except Exception as e:
            ret = parse_except(e)
        return ret
    
    def __get_reexchange(self):
        try:
            maxtimes = 5
            rpcparams = {}
            #transactions that should be __get_reexchange(dbv2b.db)
            
            ## btcfailed 
            if stmanage.get_max_times(self._name) > 0:
                maxtimes = stmanage.get_max_times(self._name)
            bflddatas = self._v2b.query_v2binfo_is_failed(maxtimes)
            if(bflddatas.state != error.SUCCEED):
                return bflddatas
            self._logger.debug("get count = {}".format(len(bflddatas.datas)))
    
            ret = self.__merge_v2b_to_rpcparams(rpcparams, bflddatas.datas)
            if(ret.state != error.SUCCEED):
                return ret
            
            ret = result(error.SUCCEED, "", rpcparams)
        except Exception as e:
            ret = parse_except(e)
        return ret


    def __get_reset_history_state_to_complete(self):
        try:
            maxtimes = 5
            rpcparams = {}
            
            ## btcfailed 
            if stmanage.get_max_times(self._name) > 0:
                maxtimes = stmanage.get_max_times(self._name)
            bflddatas = self._v2b.query_v2binfo_is_succeed(maxtimes)
            if(bflddatas.state != error.SUCCEED):
                return bflddatas
            self._logger.debug("get count = {}".format(len(bflddatas.datas)))
    
            ret = self.__merge_v2b_to_rpcparams(rpcparams, bflddatas.datas)
            if(ret.state != error.SUCCEED):
                return ret
            
            ret = result(error.SUCCEED, "", rpcparams)
        except Exception as e:
            ret = parse_except(e)
        return ret
    def __checks(self):
        assert (len(stmanage.get_sender_address_list(self._name, self.btc_chain())) > 0), "btc senders is invalid"
        assert (len(self._module_address) == 64), "module_address is invalid"
        assert (len(stmanage.get_receiver_address_list(self._name, self.proof_chain())) > 0), "violas server is invalid."
        for violas_receiver in stmanage.get_receiver_address_list(self._name, self.proof_chain()):
            assert len(violas_receiver) == 64, "violas receiver({}) is invalid".format(violas_receiver)
    
        for sender in stmanage.get_sender_address_list(self._name, self.btc_chain()):
            assert len(sender) >= 20, "btc address({}) is invalied".format(sender)
    
    def __get_btc_sender_address(self, excludeds, amount, gas):
        try:
            use_sender = None
            for sender in stmanage.get_sender_address_list(self._name, self.btc_chain()):
                if sender not in excludeds:
                   #check btc amount
                   ret = self._bclient.has_btc_banlance(sender, amount, gas)
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
            ret = parse_except(e)
        return ret
    
    def stop(self):
        self.work_stop()

    def rechange_db_state(self):
        try:
            ##update violas blockchain state to end, if sendexproofmark is ok
            tran_data = self._vclient.create_data_for_end(self.proof_chain(), self.name(), tran_id)
            ret = self._vclient.send_violas_coin(receiver, stmanage.get_combine_address_list(self.name)[0], 1, self._module_address, tran_data)
            if ret.state == error.SUCCEED:
                ret = self._v2b.update_v2binfo_to_complete_commit(tran_id)
                assert (ret.state == error.SUCCEED), "db error"
        except Exception as e:
            ret = parse_except(e)
        return ret

    def reexchange_data_from_failed(self, gas = 1000):
        try:
            #get all excluded info from db
            rpcparams = {}
            ret = self.__get_reexchange()
            if(ret.state != error.SUCCEED):
                return ret
            rpcparams = ret.datas
            receivers = list(set(stmanage.get_receiver_address_list(self._name, self.proof_chain())))

            #modulti receiver, one-by-one
            for receiver in receivers:
                if (self.work() == False):
                    break

                ret = self._v2b.query_latest_version(receiver, self._module_address)
                assert ret.state == error.SUCCEED, "get latest version error"
                latest_version = ret.datas + 1
                max_version = 0
    
                #get old transaction from db, check transaction. version and receiver is current value
                failed = rpcparams.get(receiver)
                if failed is not None:
                    self._logger.debug("start exchange failed datas from db. receiver={}".format(receiver))
                    for data in failed:
                        if (self.work() == False):
                            break

                        vaddress    = data["vaddress"]
                        vamount     = data["vamount"]
                        fmtamount   = float(vamount) / COINS
                        sequence    = int(data["sequence"])
                        version     = int(data["version"])
                        baddress    = data["baddress"]
                        module_old  = data["vtoken"]
                        vreceiver   = data["vreceiver"]
                        times       = data["times"]
                        tran_id     = data["tran_id"]
    
                        self._logger.debug(f"start exchange v2b(times={times}), datas from db. receiver = {receiver}, vaddress={vaddress} sequence={sequence} baddress={baddress} {fmtamount: .8f}") 
    
                        #check version, get transaction list is ordered ?
                        #if version >= (latest_version - 1):
                        #    continue
    
                        #match module 
                        if module_old != self._module_address:
                            self._logger.debug("module is not match.")
                            ret = self._v2b.update_v2binfo_to_failed_commit(tran_id)
                            assert (ret.state == error.SUCCEED), "db error"
                            continue
    
                        #not found , process next
                        ret = self._vserver.has_transaction(vaddress, module_old, baddress, sequence, vamount, version, vreceiver)
                        if ret.state != error.SUCCEED or ret.datas != True:
                            self._logger.debug("not found transaction from violas server.")
                            ret = self._v2b.update_v2binfo_to_failed_commit(tran_id)
                            assert (ret.state == error.SUCCEED), "db error"
                            continue
    
                        #get btc sender from stmanage.get_sender_address_list(self._name, self.btc_chain())
                        ret = self.__get_btc_sender_address([baddress], vamount, gas) #vamount and gas unit is satoshi
                        if ret.state != error.SUCCEED:
                            self._logger.debug("not found btc sender. check btc address and amount")
                            continue
                        sender = ret.datas
    
                        #send btc and mark it in OP_RETURN
                        ret = self._bclient.sendexproofmark(sender, baddress, fmtamount, vaddress, sequence, version)
                        txid = ret.datas
                        self._logger.debug(f"txid={txid}")
                        #update db state
                        if ret.state == error.SUCCEED:
                            ret = self._v2b.update_v2binfo_to_succeed_commit(tran_id, txid)
                            assert (ret.state == error.SUCCEED), "db error"
                        else:
                            ret = self._v2b.update_v2binfo_to_failed_commit(tran_id)
                            assert (ret.state == error.SUCCEED), "db error"


            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret 
    def start(self):
    
        try:
            self._logger.debug("start works")
    
            #requirement checks
            self.__checks()
    
            gas = 1000
            self.reexchange_data_from_failed(gas)
    
            receivers = list(set(stmanage.get_receiver_address_list(self._name, self.proof_chain())))
            #modulti receiver, one-by-one
            for receiver in receivers:
                if (self.work() == False):
                    break

                ret = self._v2b.query_latest_version(receiver, self._module_address)
                assert ret.state == error.SUCCEED, "get latest version error"
                latest_version = ret.datas + 1
                max_version = 0

                #get new transaction from violas server
                ret = self._vserver.get_transactions_for_start(receiver, self._module_address, latest_version)
                if ret.state == error.SUCCEED and len(ret.datas) > 0:
                    self._logger.debug("start exchange datas from violas server. receiver={}".format(receiver))
                    for data in ret.datas:
                        if (self.work() == False):
                            break

                        #grant vbtc 
                        ##check 
                        vaddress    = data["address"]
                        vamount     = int(data["amount"]) 
                        fmtamount   = float(vamount) / COINS
                        sequence    = data["sequence"] 
                        version     = data["version"]
                        baddress    = data["baddress"]
                        tran_id     = data["tran_id"]
    
                        self._logger.debug("start exchange v2b. receiver = {}, vaddress={} sequence={} baddress={} amount={} \
                                datas from server.".format(receiver, vaddress, sequence, baddress, fmtamount))
    
                        max_version = max(version, max_version)

                        #data is save to db, so must be update max version
                        ret = self._v2b.update_or_insert_version_commit(receiver, self._module_address, max_version)
                        assert (ret.state == error.SUCCEED), "db error"
    
                        #if found transaction in v2b.db, then get_transactions's latest_version is error(too small or other case)'
                        ret = self._v2b.has_v2binfo(tran_id)
                        assert ret.state == error.SUCCEED, "has_v2binfo(vaddress={}, sequence={}) failed.".format(vaddress, sequence)
                        if ret.datas == True:
                            self._logger.info("found transaction(vaddress={}, sequence={}) in db. ignore it and process next.".format(vaddress, sequence))
                            continue
    
                        #get btc sender from btc senders
                        ret = self.__get_btc_sender_address([baddress], fmtamount, gas)
                        if ret.state != error.SUCCEED:
                            self._logger.debug("not found btc sender or amount too low. check btc address and amount")
                            ret = self._v2b.insert_v2binfo_commit("", "", baddress, vamount, vaddress, sequence, version, vamount, self._module_address, receiver, dbv2b.state.FAILED, tran_id)
                            assert (ret.state == error.SUCCEED), "db error"

                            continue
                        sender = ret.datas
    
                        ##send btc transaction and mark to OP_RETURN
                        ret = self._bclient.sendexproofmark(sender, baddress, fmtamount, vaddress, sequence, version)
                        txid = ret.datas

                        #save db amount is satoshi, so db value's violas's amount == btc's amount 
                        if ret.state != error.SUCCEED:
                            ret = self._v2b.insert_v2binfo_commit("", sender, baddress, vamount, vaddress, sequence, version, vamount, self._module_address, receiver, dbv2b.state.FAILED, tran_id)
                            assert (ret.state == error.SUCCEED), "db error"
                            continue
                        else:
    
                            ret = self._v2b.insert_v2binfo_commit(txid, sender, baddress, vamount, vaddress, sequence, version, vamount, self._module_address, receiver, dbv2b.state.SUCCEED, tran_id)
                            assert (ret.state == error.SUCCEED), "db error"

                        
    
            ret = result(error.SUCCEED) 
    
        except Exception as e:
            ret = parse_except(e)
        finally:
            self._logger.info("works end.")
    
        return ret
    
def main():
       logger = log.logger.getlogger(name) 
       logger.debug("start main")
       v2b = exv2b()
       
       ret = v2b.start()
       if ret.state != error.SUCCEED:
           logger.error(ret.message)

if __name__ == "__main__":
    main()
