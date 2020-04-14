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
import vlsopt.violasclient
from vlsopt.violasclient import violasclient, violaswallet, violasserver
from vlsopt.violasproof import violasproof
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from baseobject import baseobject
from enum import Enum
from vrequest.request_client import requestclient

#module self.name
mod_name="v2b"
wallet_name = "vwallet"

COINS = comm.values.COINS
VIOLAS_ADDRESS_LEN = comm.values.VIOLAS_ADDRESS_LEN
#load logging
class exv2b(baseobject):    
    def __init__(self, name, vnodes , bnode, proofdb, module, receivers, chain = "violas"):
        baseobject.__init__(self, name)
        self._latest_version = {}
        self.set_from_chain(chain)
        self.set_map_chain("btc")
        self._vclient = violasproof(name, vnodes)
        #btc init
        self._bclient = btcclient(name, bnode)
        self._v2b = dbv2b(name, f"{self.from_chain()}_{self.name()}.db")
        self._wallet = violaswallet(name, wallet_name)
    
        #violas init
        #vserver = violasserver(self.name(), stmanage.get_violas_servers())
        self._vserver = requestclient(name, proofdb)
        self._module_address = module
        self._receivers = receivers

    def __del__(self):
        del self._vclient
        del self._bclient
        del self._work
        del self._v2b
        del self._vserver
        del self._receivers

    def __merge_v2b_to_rpcparams(self, rpcparams, dbinfos):
        try:
            self._logger.debug("start __merge_v2b_to_rpcparams")
            for info in dbinfos:
                new_data = {"vaddress":info.vaddress, "sequence":info.sequence, "vtoken":info.vtoken,\
                        "version":info.version, "to_address":info.toaddress, "vreceiver":info.vreceiver, \
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
            bflddatas = self._v2b.query_v2binfo_is_vsucceed(maxtimes)
            if(bflddatas.state != error.SUCCEED):
                return bflddatas
    
            ret = self.__merge_v2b_to_rpcparams(rpcparams, bflddatas.datas)
            if(ret.state != error.SUCCEED):
                return ret
            
            ret = result(error.SUCCEED, "", rpcparams)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def _rechange_db_state(self):
        try:
            ##update violas blockchain state to end, if sendexproofmark is ok
            ret = self.__get_reset_history_state_to_complete()
            if ret.state != error.SUCCEED:
                return ret
            
            for key in ret.datas.keys():
                if key not in self._receivers:
                    continue

                datas = ret.datas.get(key)
                for data in datas:
                    tran_id = data.get("tran_id")
                    if tran_id is None:
                        continue
                    ret = self._vserver.is_end(tran_id)
                    if ret.state == error.SUCCEED and ret.datas == True:
                       ret = self._v2b.update_v2binfo_to_complete_commit(tran_id)
                       assert (ret.state == error.SUCCEED), "db error"

        except Exception as e:
            ret = parse_except(e)
        return ret

    def __get_reset_history_state_to_resend_tran(self):
        try:
            maxtimes = 5
            rpcparams = {}
            
            ## btcfailed 
            if stmanage.get_max_times(self._name) > 0:
                maxtimes = stmanage.get_max_times(self._name)
            vfdatas = self._v2b.query_v2binfo_is_vfailed(maxtimes)
            if(vfdatas.state != error.SUCCEED):
                return vfdatas
    
            ret = self.__merge_v2b_to_rpcparams(rpcparams, vfdatas.datas)
            if(ret.state != error.SUCCEED):
                return ret
            
            sudatas = self._v2b.query_v2binfo_is_succeed(maxtimes)
            if(sudatas.state != error.SUCCEED):
                return sudatas
    
            ret = self.__merge_v2b_to_rpcparams(rpcparams, sudatas.datas)
            if(ret.state != error.SUCCEED):
                return ret
            
            ret = result(error.SUCCEED, "", rpcparams)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def _rechange_violas_state(self):
            ##update violas blockchain state to end, if sendexproofmark is ok
            ret_datas = self.__get_reset_history_state_to_resend_tran()
            if ret_datas.state != error.SUCCEED:
                return ret_datas
            
            for receiver in ret_datas.datas.keys():
                if not self.work() :
                    break

                if receiver not in self._receivers:
                    continue
                
                ret  = self._wallet.get_account(receiver)
                if ret.state != error.SUCCEED:
                    continue
                vsender = ret.datas

                datas = ret_datas.datas.get(receiver)
                for data in datas:
                    tran_id = data.get("tran_id")
                    module = data.get("vtoken")
                    if tran_id is None:
                        continue
                    #state is end? maybe changing state rasise except, but transaction is SUCCEED
                    ret = self._vserver.is_end(tran_id)
                    if ret.state == error.SUCCEED and ret.datas == True:
                       ret = self._v2b.update_v2binfo_to_complete_commit(tran_id)
                       assert (ret.state == error.SUCCEED), "db error"
                       continue

                    if module != self._module_address:
                        continue
                    #sendexproofmark succeed , change violas state
                    self._send_violas_coin_and_update_state_to_end(vsender, receiver, module, tran_id)

    def _send_violas_coin_and_update_state_to_end(self, vsender, receiver, module,  tran_id, amount = 1):
            tran_data = self._vclient.create_data_for_end(self.from_chain(), self.name(), tran_id)
            ret = self._vclient.send_violas_coin(vsender, receiver, amount, module, tran_data)
            if ret.state == error.SUCCEED:
                ret = self._v2b.update_v2binfo_to_vsucceed_commit(tran_id)
                assert (ret.state == error.SUCCEED), "db error"
            return ret
        
    def __checks(self):
        assert (len(stmanage.get_sender_address_list(self._name, self.map_chain())) > 0), "btc senders is invalid"
        assert (len(self._module_address) in VIOLAS_ADDRESS_LEN), "module_address is invalid"
        assert (len(stmanage.get_receiver_address_list(self._name, self.from_chain())) > 0), "violas server is invalid."
        for violas_receiver in stmanage.get_receiver_address_list(self._name, self.from_chain()):
            assert len(violas_receiver) in VIOLAS_ADDRESS_LEN, "violas receiver({}) is invalid".format(violas_receiver)
    
        for sender in stmanage.get_sender_address_list(self._name, self.map_chain()):
            assert len(sender) >= 20, "btc address({}) is invalied".format(sender)
    
    def __get_btc_sender_address(self, excludeds, amount, gas):
        try:
            use_sender = None
            for sender in stmanage.get_sender_address_list(self._name, self.map_chain()):
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
        try:
            self._vclient.stop()
            self.work_stop()
            pass
        except Exception as e:
            parse_except(e)

    def reexchange_data_from_failed(self, gas = 1000):
        try:
            #get all excluded info from db
            rpcparams = {}
            ret = self.__get_reexchange()
            if(ret.state != error.SUCCEED):
                return ret
            rpcparams = ret.datas
            receivers = self._receivers

            #modulti receiver, one-by-one
            for receiver in receivers:
                if not self.work() :
                    break
    
                ret  = self._wallet.get_account(receiver)
                if ret.state != error.SUCCEED:
                    continue 
                vsender = ret.datas

                latest_version = self._latest_version.get(receiver, -1)

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
                        baddress    = data["to_address"]
                        module      = data["vtoken"]
                        vreceiver   = data["vreceiver"]
                        times       = data["times"]
                        tran_id     = data["tran_id"]
    
                        self._logger.info(f"start exchange v2b(times={times}), datas from db. \
                                receiver = {receiver}, vaddress={vaddress} sequence={sequence} to_address={baddress} \
                                {fmtamount: .8f} version={version} module={module} tran_id={tran_id}") 
    
                        #check version, get transaction list is ordered ?
                        if version > latest_version:
                            self._logger.warning(f"transaction's version must be Less than or equal to latest_version.")
                            continue
    
                        #match module 
                        if module != self._module_address:
                            self._logger.warning(f"module is not match. {module}<->{self._module_address}")
                            continue
    
                        #not found , process next
                        ret = self._vserver.has_transaction(vaddress, module, baddress, sequence, vamount, version, vreceiver)
                        if ret.state != error.SUCCEED or ret.datas != True:
                            self._logger.warning(f"not found transaction({data}) from violas server.")
                            continue
    
                        #get btc sender from stmanage.get_sender_address_list(self._name, self.map_chain())
                        ret = self.__get_btc_sender_address([baddress], vamount, gas) #vamount and gas unit is satoshi
                        if ret.state != error.SUCCEED:
                            self._logger.warning("not found btc sender{baddress} or amount too low. check btc address and amount")
                            continue
                        sender = ret.datas
    
                        #send btc and mark it in OP_RETURN
                        ret = self._bclient.sendexproofmark(sender, baddress, fmtamount, vaddress, sequence, version)
                        txid = ret.datas
                        #update db state
                        if ret.state == error.SUCCEED:
                            ret = self._v2b.update_v2binfo_to_succeed_commit(tran_id, txid)
                            assert (ret.state == error.SUCCEED), "db error"
                        else:
                            ret = self._v2b.update_v2binfo_to_failed_commit(tran_id)
                            assert (ret.state == error.SUCCEED), "db error"
                            continue

                        #sendexproofmark succeed , change violas state
                        self._send_violas_coin_and_update_state_to_end(vsender, receiver, module, tran_id)

            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret 
    def start(self):
    
        try:
            self._logger.debug("start works")
            gas = 1000

            #requirement checks
            self.__checks()
    
            #db state: VFAILED
            #send btc is succeed, but change transaction state is failed, 
            ##so re send violas transaction to change state = end
            self._rechange_violas_state()

            #db state: FAILED
            #if history datas is found state = failed, exchange it until succeed
            self.reexchange_data_from_failed(gas)
    
            #db state: SUCCEED
            #check state from violas blockchain, and change exchange history data, 
            ##when change it to complete, can truncature history db
            self._rechange_db_state()

            receivers = list(set(stmanage.get_receiver_address_list(self._name, self.from_chain())))
            #modulti receiver, one-by-one
            for receiver in receivers:
                if not self.work() :
                    break

                ret  = self._wallet.get_account(receiver)
                if ret.state != error.SUCCEED:
                    continue
                vsender = ret.datas

                latest_version = self._latest_version.get(receiver, 0) + 1

                #get new transaction from violas server
                ret = self._vserver.get_transactions_for_start(receiver, self._module_address, latest_version)
                if ret.state == error.SUCCEED and len(ret.datas) > 0:
                    self._logger.debug("start exchange datas from violas server. receiver={}".format(receiver))
                    for data in ret.datas:
                        if not self.work() :
                            break

                        #grant vbtc 
                        ##check 
                        vaddress    = data["address"]
                        vamount     = int(data["amount"]) 
                        fmtamount   = float(vamount) / COINS
                        sequence    = data["sequence"] 
                        version     = data["version"]
                        baddress    = data["to_address"]
                        tran_id     = data["tran_id"]
    
                        self._logger.info(f"start exchange v2b. receiver = {receiver}, vaddress={vaddress} sequence={sequence} \
                                baddress={baddress} amount={fmtamount} tran_id={tran_id} datas from server.")
    
                        latest_version = self._latest_version.get(receiver, -1)
                        self._latest_version[receiver] = max(version, latest_version)
    
                        #if found transaction in v2b.db, then get_transactions's latest_version is error(too small or other case)'
                        ret = self._v2b.has_v2binfo(tran_id)
                        assert ret.state == error.SUCCEED, "has_v2binfo(vaddress={}, sequence={}) failed.".format(vaddress, sequence)
                        if ret.datas == True:
                            self._logger.warning("found transaction(tran_id = {tran_id})) in db. ignore it and process next.".format(vaddress, sequence))
                            continue
    
                        #get btc sender from btc senders
                        ret = self.__get_btc_sender_address([baddress], fmtamount, gas)
                        if ret.state != error.SUCCEED:
                            self._logger.warning("not found btc sender{baddress} or amount too low. check btc address and amount")
                            ret = self._v2b.insert_v2binfo_commit("", "", baddress, vamount, vaddress, sequence, \
                                    version, vamount, self._module_address, receiver, dbv2b.state.FAILED, tran_id)
                            assert (ret.state == error.SUCCEED), "db error"
                            continue
                        sender = ret.datas
    
                        ##send btc transaction and mark to OP_RETURN
                        ret = self._bclient.sendexproofmark(sender, baddress, fmtamount, vaddress, sequence, version)
                        txid = ret.datas

                        #save db amount is satoshi, so db value's violas's amount == btc's amount 
                        if ret.state != error.SUCCEED:
                            ret = self._v2b.insert_v2binfo_commit("", sender, baddress, vamount, vaddress, sequence, \
                                    version, vamount, self._module_address, receiver, dbv2b.state.FAILED, tran_id)
                            assert (ret.state == error.SUCCEED), "db error"
                            continue
                        else:
                            ret = self._v2b.insert_v2binfo_commit(txid, sender, baddress, vamount, vaddress, sequence, \
                                    version, vamount, self._module_address, receiver, dbv2b.state.SUCCEED, tran_id)
                            assert (ret.state == error.SUCCEED), "db error"
           
                        #sendexproofmark succeed , change violas state
                        self._send_violas_coin_and_update_state_to_end(vsender, receiver, self._module_address, tran_id)
    
            ret = result(error.SUCCEED) 
    
        except Exception as e:
            ret = parse_except(e)
        finally:
            self._logger.debug("works end.")
    
        return ret
    
def main():
       print("start main")
       v2b = exv2b()
       
       ret = v2b.start()
       if ret.state != error.SUCCEED:
           print(ret.message)

if __name__ == "__main__":
    main()
