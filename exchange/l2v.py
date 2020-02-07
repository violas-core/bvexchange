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
name="l2v"
wallet_name = "vwallet"

COINS = comm.values.COINS
#load logging
class exv2b(baseobject):    
    def __init__(self, name, fromnodes , mapnodes, proofdb, module, receivers, senders, fromchain = "libra", mapchain='violas'):
        baseobject.__init__(self, name)
        self.set_proof_chain(fromchain)
        self._fromclient = violasproof(name, fromnodes, fromchain)
        self._mapclient = violasproof(name, mapnodes, mapchain)
        self._db = dbl2v(name, f"{self.proof_chain()}_{self.name()}.db")
        self._wallet = violaswallet(name, wallet_name)
    
        #violas/libra init
        self._pserver = requestclient(name, proofdb)
        self._module_address = module
        self._receivers = receivers
        self._senders = senders

    def __del__(self):
        del self._fromclient
        del self._mapclient
        del self._work
        del self._db
        del self._pserver
        del self._receivers

    def __get_map_sender_address(amount, module=None, gas=28_000):
        try:
            sender_account = None
            for sender in self._senders:
                sender_account = self._wallet.get_account(sender)
                break
            ret = result(error.SUCCEED, "", sender_account)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def __merge_db_to_rpcparams(self, rpcparams, dbinfos):
        try:
            self._logger.debug("start __merge_db_to_rpcparams")
            for info in dbinfos:
                new_data = {"sender":info.sender, "receiver":info.receiver, "sequence":info.sequence, \
                        "version":info.version, "module":info.module, "to_address":info.toaddress,  \
                        "fromaddress":"fromaddress", "amount":info.amount, "times":info.times, "tran_id":info.tranid}
                if info.toaddress in rpcparams.keys():
                    rpcparams[info.toaddress].append(new_data)
                else:
                    rpcparams[info.toaddress] = [new_data]
    
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
            bflddatas = self._db.query_is_failed(maxtimes)
            if(bflddatas.state != error.SUCCEED):
                return bflddatas
    
            ret = self.__merge_db_to_rpcparams(rpcparams, bflddatas.datas)
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
            bflddatas = self._v2b.query_is_vsucceed(maxtimes)
            if(bflddatas.state != error.SUCCEED):
                return bflddatas
    
            ret = self.__merge_db_to_rpcparams(rpcparams, bflddatas.datas)
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
                    ret = self._pserver.is_end(tran_id)
                    if ret.state == error.SUCCEED and ret.datas == True:
                       ret = self._db.update_to_complete_commit(tran_id)
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
            vfdatas = self._db.query_is_vfailed(maxtimes)
            if(vfdatas.state != error.SUCCEED):
                return vfdatas
    
            ret = self.__merge_db_to_rpcparams(rpcparams, vfdatas.datas)
            if(ret.state != error.SUCCEED):
                return ret
            
            sudatas = self._db.query_db_is_succeed(maxtimes)
            if(sudatas.state != error.SUCCEED):
                return sudatas
    
            ret = self.__merge_db_to_rpcparams(rpcparams, sudatas.datas)
            if(ret.state != error.SUCCEED):
                return ret
            
            ret = result(error.SUCCEED, "", rpcparams)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def _rechange_tran_state(self):
            ##update violas/libra blockchain state to end, if sendexproofmark is ok
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
                sender = ret.datas

                datas = ret_datas.datas.get(receiver)
                for data in datas:
                    tran_id = data.get("tran_id")
                    module = data.get("module")
                    if tran_id is None:
                        continue
                    #state is end? maybe changing state rasise except, but transaction is SUCCEED
                    ret = self._pserver.is_end(tran_id)
                    if ret.state == error.SUCCEED and ret.datas == True:
                       ret = self._db.update_to_complete_commit(tran_id)
                       assert (ret.state == error.SUCCEED), "db error"
                       continue

                    if module != self._module_address:
                        continue
                    #sendexproofmark succeed , change violas state
                    self._send_coin_and_update_state_to_end(sender, receiver, module, tran_id)

    def _send_coin_for_update_state_to_end(self, sender, receiver, module,  tran_id, amount = 1):
            tran_data = self._fromclient.create_data_for_end(self.proof_chain(), self.name(), tran_id)
            if module is None:
                ret = self._fromclient.send_platform_coin(sender, receiver, amount,  tran_data)
            else: 
                ret = self._fromclient.send_violas_coin(sender, receiver, amount, module, tran_data)
            if ret.state == error.SUCCEED:
                ret = self._db.update_to_vsucceed_commit(tran_id)
                assert (ret.state == error.SUCCEED), "db error"
            return ret
        
    def __checks(self):
        assert (len(stmanage.get_sender_address_list(self._name, self.btc_chain())) > 0), "btc senders is invalid"
        assert (len(self._module_address) == 64), "module_address is invalid"
        assert (len(stmanage.get_receiver_address_list(self._name, self.proof_chain())) > 0), "violas server is invalid."
        for violas_receiver in stmanage.get_receiver_address_list(self._name, self.proof_chain()):
            assert len(violas_receiver) == 64, "violas receiver({}) is invalid".format(violas_receiver)
    
        for sender in stmanage.get_sender_address_list(self._name, self.btc_chain()):
            assert len(sender) >= 20, "btc address({}) is invalied".format(sender)
    
    def stop(self):
        try:
            self._mapclient.stop()
            self._fromclient.stop()
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

                ret = self._db.query_latest_version(receiver, self._module_address)
                assert ret.state == error.SUCCEED, "get latest version error"
                latest_version = ret.datas + 1
                max_version = 0
    
                ret  = self._wallet.get_account(receiver)
                if ret.state != error.SUCCEED:
                    continue 
                mapsender = ret.datas

                #get old transaction from db, check transaction. version and receiver is current value
                failed = rpcparams.get(receiver)
                if failed is not None:
                    self._logger.debug("start exchange failed datas from db. receiver={}".format(receiver))
                    for data in failed:
                        if (self.work() == False):
                            break

                        toaddress   = data["receiver"]
                        vamount     = data["amount"]
                        sequence    = int(data["sequence"])
                        version     = int(data["version"])
                        module      = data["module"]
                        times       = data["times"]
                        tran_id     = data["tran_id"]
    
                        self._logger.info(f"start exchange exglv, datas from db. toaddress={toaddress}, sequence={sequence} \
                                version={version}, receiver={receiver}, amount={amount}, module={module}, tran_id={tran_id} datas from server.")

                        #check version, get transaction list is ordered ?
                        #if version >= (latest_version - 1):
                        #    continue
    
                        #match module 
                        if module != self._module_address:
                            self._logger.warning(f"module is not match. {module}<->{self._module_address}")
                            continue
    
                        #not found , process next
                        ret = self._vserver.has_transaction(fromaddress, module, baddress, sequence, vamount, version, vreceiver)
                        if ret.state != error.SUCCEED or ret.datas != True:
                            self._logger.warning(f"not found transaction({data}) from violas server.")
                            continue
    
                        #get map sender from btc senders
                        ret = self.__get_map_sender_address(amount)
                        if ret.state != error.SUCCEED:
                            continue
                        mapsender = ret.datas
    
                        ##send btc transaction and mark to OP_RETURN
                        tran_data = self._mapclient.create_data_for_mark("violas", "l2v", "version", version)
                        ret = self._mapclient.send_violas_coin(mapsender, toaddress, amount, module, tran_data)
                        #update db state
                        if ret.state == error.SUCCEED:
                            ret = self._db.update_to_succeed_commit(tran_id)
                            assert (ret.state == error.SUCCEED), "db error"
                        else:
                            ret = self._db.update_to_failed_commit(tran_id)
                            assert (ret.state == error.SUCCEED), "db error"
                            continue

                        #sendexproofmark succeed , send violas/libra coin with data for change violas state
                        self._send_violas_coin_and_update_state_to_end(fromsender, receiver, module, tran_id)

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

            receivers = list(set(stmanage.get_receiver_address_list(self._name, self.proof_chain())))
            #modulti receiver, one-by-one
            for receiver in receivers:
                if not self.work() :
                    break

                ret  = self._wallet.get_account(receiver)
                if ret.state != error.SUCCEED:
                    continue
                fromsender = ret.datas

                ret = self._db.query_latest_version(receiver, self._module_address)
                assert ret.state == error.SUCCEED, "get latest version error"
                latest_version = ret.datas + 1
                max_version = 0

                #get new transaction from violas server
                ret = self._pserver.get_transactions_for_start(receiver, self._module_address, latest_version)
                if ret.state == error.SUCCEED and len(ret.datas) > 0:
                    self._logger.debug("start exchange datas from violas/libra server. receiver={}".format(receiver))
                    for data in ret.datas:
                        if not self.work() :
                            break

                        #grant vbtc 
                        ##check 
                        fromaddress = data["address"]
                        amount      = int(data["amount"]) 
                        sequence    = data["sequence"] 
                        version     = data["version"]
                        toaddress   = data["to_address"]
                        tran_id     = data["tran_id"]
    
                        self._logger.info(f"start exchange l2v.sender={fromaddress},  receiver={receiver}, sequence={sequence} \
                                version={version}, toaddress={toaddress}, amount={amount}, tran_id={tran_id} datas from server.")
    
                        max_version = max(version, max_version)

                        #data is save to db, so must be update max version
                        ret = self._db.update_or_insert_version_commit(receiver, self._module_address, max_version)
                        assert (ret.state == error.SUCCEED), "db error"
    
                        #if found transaction in history.db, then get_transactions's latest_version is error(too small or other case)'
                        ret = self._db.has_info(tran_id)
                        assert ret.state == error.SUCCEED, f"has_info(fromaddress={fromaddress}, sequence={sequence}, version={version}) failed."
                        if ret.datas == True:
                            self._logger.warning(f"found transaction(tran_id = {tran_id})) in db. ignore it and process next."
                            continue
    
                        #get map sender from btc senders
                        ret = self.__get_map_sender_address(amount)
                        if ret.state != error.SUCCEED:
                            self._logger.warning("not found map sender{toaddress} or amount too low. check address and amount")
                            ret = self._db.insert_commit( "", toaddress, sequence, \
                                    version, amount, self._module_address, fromaddress, receiver, dbl2v.state.FAILED, tran_id)
                            assert (ret.state == error.SUCCEED), "db error"
                            continue
                        mapsender = ret.datas
    
                        ##send btc transaction and mark to OP_RETURN
                        tran_data = self._mapclient.create_data_for_mark("violas", "l2v", "version", version)
                        ret = self._mapclient.send_violas_coin(mapsender, toaddress, amount, module, tran_data)

                        if ret.state != error.SUCCEED:
                            ret = self._db.insert_commit( "", toaddress, sequence, \
                                    version, amount, self._module_address, fromaddress, receiver, db.state.FAILED, tran_id)
                            assert (ret.state == error.SUCCEED), "db error"
                            continue
                        else:
                            ret = self._db.insert_commit( sender, toaddress, sequence, \
                                    version, amount, self._module_address, fromaddress, receiver, db.state.SUCCEED, tran_id)
                            assert (ret.state == error.SUCCEED), "db error"
           
                        #sendexproofmark succeed , send violas/libra coin with data for change violas state
                        self._send_coin_for_update_state_to_end(fromsender, receiver, self._module_address, tran_id)
    
            ret = result(error.SUCCEED) 
    
        except Exception as e:
            ret = parse_except(e)
        finally:
            self._logger.debug("works end.")
    
        return ret
    
def main():
       print("start main")
       l2v = exl2v()
       
       ret = l2v.start()
       if ret.state != error.SUCCEED:
           print(ret.message)

if __name__ == "__main__":
    main()
