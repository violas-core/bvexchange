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
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from baseobject import baseobject
from enum import Enum

#module self.name
name="v2b"

COINS = comm.values.COINS
#load logging
class exv2b(baseobject):    
    def __init__(self, name="v2b", work=True):
        baseobject.__init__(self, name, work)

    def __merge_v2b_to_rpcparams(self, rpcparams, dbinfos):
        try:
            self._logger.debug("start __merge_v2b_to_rpcparams")
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
            ret = parse_except(e)
        return ret
    
    def __get_reexchange(self, v2b):
        try:
            maxtimes = 5
            rpcparams = {}
            #transactions that should be __get_reexchange(dbv2b.db)
            
            ## btcfailed 
            if stmanage.get_max_times(self._name) > 0:
                maxtimes = stmanage.get_max_times(self._name)
            bflddatas = v2b.query_v2binfo_is_failed(maxtimes)
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
        assert (len(stmanage.get_btc_conn()) == 4), "btc_conn is invalid."
        assert (len(stmanage.get_sender_address_list(self._name, self._btc_chain)) > 0), "btc senders is invalid"
        assert (len(stmanage.get_module_address(self._name, self._violas_chain)) == 64), "module_address is invalid"
        assert (len(stmanage.get_violas_servers()) > 0), "violas_nodes is invalid."
        assert (len(stmanage.get_receiver_address_list(self._name, self._violas_chain)) > 0), "violas server is invalid."
        for violas_receiver in stmanage.get_receiver_address_list(self._name, self._violas_chain):
            assert len(violas_receiver) == 64, "violas receiver({}) is invalid".format(violas_receiver)
    
        for sender in stmanage.get_sender_address_list(self._name, self._btc_chain):
            assert len(sender) >= 20, "btc address({}) is invalied".format(sender)
    
    def __get_btc_sender_address(self, bclient, excludeds, amount, gas):
        try:
            use_sender = None
            for sender in stmanage.get_sender_address_list(self._name, self._btc_chain):
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
            ret = parse_except(e)
        return ret
    
    def stop(self):
        self.work_stop()

    def start(self):
    
        try:
            self._logger.debug("start works")
            dbv2b_name = "bve_v2b.db"
            wallet_name = "vwallet"
    
            #requirement checks
            self.__checks()
    
            #btc init
            bclient = btcclient(self.name(), stmanage.get_btc_conn())
            v2b = dbv2b(self.name(), dbv2b_name)
    
            #violas init
            vserver = violasserver(self.name(), stmanage.get_violas_servers())
    
            module_address = stmanage.get_module_address(self._name, self._violas_chain)
    
            gas = 1000
            
            #get all excluded info from db
            rpcparams = {}
            ret = self.__get_reexchange(v2b)
            if(ret.state != error.SUCCEED):
                return ret
            rpcparams = ret.datas
    
            receivers = list(set(stmanage.get_receiver_address_list(self._name, self._violas_chain)))
            #modulti receiver, one-by-one
            for receiver in receivers:
                if (self.work() == False):
                    break

                ret = v2b.query_latest_version(receiver, module_address)
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

                        vaddress = data["vaddress"]
                        vamount = data["vamount"]
                        fmtamount = float(vamount) / COINS
                        sequence = int(data["sequence"])
                        version = int(data["version"])
                        baddress = data["baddress"]
                        module_old = data["vtoken"]
                        vreceiver = data["vreceiver"]
                        times    = data["times"]
    
                        self._logger.debug(f"start exchange v2b(times={times}), datas from db. receiver = {receiver}, vaddress={vaddress} sequence={sequence} baddress={baddress} {fmtamount: .8f}") 
    
                        #check version, get transaction list is ordered ?
                        #if version >= (latest_version - 1):
                        #    continue
    
                        #match module 
                        if module_old != module_address:
                            self._logger.debug("module is not match.")
                            ret = v2b.update_v2binfo_to_failed_commit(vaddress, sequence, version)
                            assert (ret.state == error.SUCCEED), "db error"
                            continue
    
                        #not found , process next
                        ret = vserver.has_transaction(vaddress, module_old, baddress, sequence, vamount, version, vreceiver)
                        if ret.state != error.SUCCEED or ret.datas != True:
                            self._logger.debug("not found transaction from violas server.")
                            ret = v2b.update_v2binfo_to_failed_commit(vaddress, sequence, version)
                            assert (ret.state == error.SUCCEED), "db error"
                            continue
    
                        #get btc sender from stmanage.get_sender_address_list(self._name, self._btc_chain)
                        ret = self.__get_btc_sender_address(bclient, [baddress], vamount, gas) #vamount and gas unit is satoshi
                        if ret.state != error.SUCCEED:
                            self._logger.debug("not found btc sender. check btc address and amount")
                            continue
                        sender = ret.datas
    
                        #send btc and mark it in OP_RETURN
                        ret = bclient.sendexproofmark(sender, baddress, fmtamount, vaddress, sequence, version)
                        txid = ret.datas
                        self._logger.debug(f"txid={txid}")
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
                    self._logger.debug("start exchange datas from violas server. receiver={}".format(receiver))
                    for data in ret.datas:
                        if (self.work() == False):
                            break

                        #grant vbtc 
                        ##check 
                        vaddress = data["address"]
                        vamount = int(data["amount"]) 
                        fmtamount = float(vamount) / COINS
                        sequence = data["sequence"] 
                        version = data["version"]
                        baddress = data["baddress"]
    
                        self._logger.debug("start exchange v2b. receiver = {}, vaddress={} sequence={} baddress={} amount={} \
                                datas from server.".format(receiver, vaddress, sequence, baddress, fmtamount))
    
                        max_version = max(version, max_version)
    
                        #if found transaction in v2b.db, then get_transactions's latest_version is error(too small or other case)'
                        ret = v2b.has_v2binfo(vaddress, sequence, version)
                        assert ret.state == error.SUCCEED, "has_v2binfo(vaddress={}, sequence={}) failed.".format(vaddress, sequence)
                        if ret.datas == True:
                            self._logger.info("found transaction(vaddress={}, sequence={}) in db. ignore it and process next.".format(vaddress, sequence))
                            continue
    
                        #get btc sender from btc senders
                        ret = self.__get_btc_sender_address(bclient, [baddress], fmtamount, gas)
                        if ret.state != error.SUCCEED:
                            self._logger.debug("not found btc sender or amount too low. check btc address and amount")
                            ret = v2b.insert_v2binfo_commit("", sender, baddress, vamount, vaddress, sequence, vamount, module_address, version, dbv2b.state.FAILED)
                            assert (ret.state == error.SUCCEED), "db error"
                            continue
                        sender = ret.datas
    
                        ##send btc transaction and mark to OP_RETURN
                        ret = bclient.sendexproofmark(sender, baddress, fmtamount, vaddress, sequence, version)
                        txid = ret.datas
                        self._logger.debug(f"txid={txid}")
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
