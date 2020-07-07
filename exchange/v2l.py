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
from db.dbv2l import dbv2l as localdb
import vlsopt.violasclient
from vlsopt.violasclient import violasclient, violaswallet, violasserver
from vlsopt.violasproof import violasproof
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from baseobject import baseobject
from enum import Enum
from vrequest.request_client import requestclient

#module self.name
#name="exlv"
wallet_name = "vwallet"

VIOLAS_ADDRESS_LEN = comm.values.VIOLAS_ADDRESS_LEN
#load logging
class exv2l(baseobject):    
    def __init__(self, name, dtype, vlsnodes, lbrnodes, proofdb, receivers, senders, combine):
        baseobject.__init__(self, name)
        self._latest_version = {}
        self.from_chain = "violas"
        self.map_chain = "libra"
        self._from_client = violasproof(name, vlsnodes, self.from_chain)
        self._map_client = violasproof(name, mapnodes, mapchain)
        self._db = localdb(name, f"{self.from_chain}_{self.name()}.db")
        self._fromwallet = violaswallet(name, wallet_name, self.from_chain)
        self._mapwallet = violaswallet(name, wallet_name, self.map_chain)
    
        #violas/libra init
        self._pserver = requestclient(name, proofdb)
        self._receivers = receivers
        self._senders = senders
        self._combine = combine
        self._dtype = dtype
        self.to_token_id = stmanage.get_type_stable_token(dtype)

    def __del__(self):
        del self._from_client
        del self._map_client
        del self._work
        del self._db
        del self._pserver
        del self._receivers

    @property
    def receivers(self):
        return self._receivers

    @property
    def combine(self):
        return self._combine

    @property
    def pserver(self):
        return self._pserver

    @property
    def dtype(self):
        return self._dtype

    @property
    def to_token_id(self):
        return self._to_token_id

    @property 
    def from_wallet(self):
        return self._fromwallet

    @property
    def map_wallet(self):
        return self._mapwallet

    @property
    def from_client(self):
        return self._from_client

    @property
    def map_client(self):
        return self._map_client

    def insert_to_localdb_with_check(self, version, state, tran_id, receiver):
        ret = self._db.insert_commit(version, localdb.state.FAILED, tran_id, receiver)
        assert (ret.state == error.SUCCEED), "db error"

    def update_localdb_state_with_check(self, tran_id, state):
        ret = self._db.update_state_commit(tran_id, state)
        assert (ret.state == error.SUCCEED), "db error"

    def __get_map_sender_address(self, amount, module=None, gas=28_000):
        try:
            sender_account = None
            for sender in self._senders:
                sender_account = self.map_wallet.get_account(sender)
                ret = result(error.SUCCEED, "", sender_account.datas)
                return ret

            return result(error.FAILED, "not found sender account")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def __check_address_token_is_enough(self, address, token_id, amount):
        try:
            ret = self.from_client.get_balance(address, token_id = token_id)
            assert ret.state == SUCCEED, f"get balance failed"
            
            cur_amount = ret.datas
            return result(error.SUCCEED, datas = cur_amount >= amount)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def __fill_address_token(self, address, token_id, amount, gas=40_000):
        try:
            ret = self.from_client.get_balance(address, token_id = token_id)
            assert ret.state == SUCCEED, f"get balance failed"
            
            cur_amount = ret.datas
            if cur_amount < amount + gas:
                ret = self.from_client.mint_coin(address, amount = amount + gas - cur_amount, token_id = token_id)
                return ret

            return result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def __merge_db_to_rpcparams(self, rpcparams, dbinfos):
        try:
            self._logger.debug("start __merge_db_to_rpcparams")
            for info in dbinfos:
                new_data = {
                        "version":info.version, "tran_id":info.tranid, "state":info.state}
                #server receiver address
                if info.toaddress in rpcparams.keys():
                    rpcparams[info.receiver].append(new_data)
                else:
                    rpcparams[info.receiver] = [new_data]
    
            return result(error.SUCCEED, "", rpcparams)
        except Exception as e:
            ret = parse_except(e)
        return ret
    
    def __load_record_and_merge(self, rpcparams, state, maxtimes = 999999999):
        try:
            ret = self._db.query_with_state(state, maxtimes)
            if(ret.state != error.SUCCEED):
                return ret 
    
            ret = self.__merge_db_to_rpcparams(rpcparams, ret.datas)
        except Exception as e:
            ret = parse_except(e)
        return ret
    def __get_reexchange(self):
        try:
            maxtimes = 5
            rpcparams = {}
            #transactions that should be __get_reexchange(xxx.db)
            
            ## failed 
            if stmanage.get_max_times(self.name()) > 0:
                maxtimes = stmanage.get_max_times(self._name)

            states = []
            states.append(localdb.state.FAILED)
            states.append(localdb.state.QBFAILED)
            states.append(localdb.state.FILLFAILED)
            states.append(localdb.state.PFAILED)
            states.append(localdb.state.VFAILED)
            states.append(localdb.state.SFAILED)
            for state in states:
                self.__load_record_and_merge(rpcparams, state, maxtimes)

            ret = result(error.SUCCEED, "", rpcparams)
        except Exception as e:
            ret = parse_except(e)
        return ret


    def __get_reset_history_state_to_complete(self):
        try:
            maxtimes = 5
            rpcparams = {}
            
            ## failed 
            if stmanage.get_max_times(self.name()) > 0:
                maxtimes = stmanage.get_max_times(self.name())
            bflddatas = self._db.query_is_vsucceed(maxtimes)
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
                datas = ret.datas.get(key)
                for data in datas:
                    tran_id = data.get("tran_id")
                    if tran_id is None:
                        continue
                    ret = self._pserver.is_end(tran_id)
                    if ret.state == error.SUCCEED and ret.datas == True:
                       ret = self.update_localdb_state_with_check(tran_id, localdb.state.COMPLETE)

                    ret = self._pserver.is_stop(tran_id)
                    if ret.state == error.SUCCEED and ret.datas == True:
                       ret = self.update_localdb_state_with_check(tran_id, localdb.state.COMPLETE)

        except Exception as e:
            ret = parse_except(e)
        return ret

    def __get_reset_history_state_to_resend_tran(self):
        try:
            maxtimes = 5
            rpcparams = {}
            
            ## failed 
            if stmanage.get_max_times(self.name()) > 0:
                maxtimes = stmanage.get_max_times(self.name())

            #change state transaction failed
            vfdatas = self._db.query_is_vfailed(maxtimes)
            if(vfdatas.state != error.SUCCEED):
                return vfdatas
    
            ret = self.__merge_db_to_rpcparams(rpcparams, vfdatas.datas)
            if(ret.state != error.SUCCEED):
                return ret
            
            sudatas = self._db.query_is_succeed(maxtimes)
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
            
            for receiver in self.receivers:
                if not self.work() :
                    break

                datas = ret_datas.datas.get(receiver)
                for his in datas:
                    tran_id = his.get("tran_id")
                    if tran_id is None:
                        continue

                    ret = self.pserver.get_tran_by_tranid(tran_id)
                    if ret.state != error.SUCCEED:
                        continue
                    data = ret.datas

                    receiver_tran = data.get("receiver")
                    if receiver != receiver_tran:
                        continue

                    stable_token_id = data.get("token_id")
                    token_id = stmanage.get_token_map(stable_token_id) #stable token -> LBRXXX token

                    #state is end? maybe changing state rasise except, but transaction is SUCCEED
                    ret = self._pserver.is_end(tran_id)
                    if ret.state == error.SUCCEED and ret.datas == True:
                       self.update_localdb_state_with_check(tran_id, localdb.state.COMPLETE)
                       continue

                    ret  = self.from_wallet.get_account(receiver)
                    if ret.state != error.SUCCEED:
                        continue
                    sender = ret.datas

                    #sendexproofmark succeed , change violas state
                    self._send_coin_for_update_state_to_end(sender, receiver, tran_id, token_id)

    def _send_coin_for_update_state_to_end(self, sender, receiver, tran_id, token_id, amount = 1):
            self._logger.debug(f"start _send_coin_for_update_state_to_end(sender={sender.address.hex()},"\
                    f"recever={receiver}, tran_id={tran_id}, amount={amount})")
            tran_data = self.from_client.create_data_for_end(self.from_chain(), self.name(), tran_id, "")
                ret = self.from_client.send_coin(sender, receiver, amount, token_id, data = tran_data)
            if ret.state != error.SUCCEED:
                self.update_localdb_state_with_check(tran_id, localdb.state.VFAILED)
            else:
                self.update_localdb_state_with_check(tran_id, localdb.state.VSUCCEED)
            return ret
        
    def __checks(self):
        assert (len(stmanage.get_sender_address_list(self.name(), self.map_chain())) > 0), f"{self.map_chain()} senders is invalid"
        for sender in stmanage.get_sender_address_list(self.name(), self.map_chain()):
            assert len(sender) in VIOLAS_ADDRESS_LEN, f"{self.map_chain()} address({f}) is invalied"

        assert (len(stmanage.get_receiver_address_list(self.name(), self.from_chain())) > 0), f"{self.from_chain()} receivers is invalid."
        for receiver in stmanage.get_receiver_address_list(self.name(), self.from_chain()):
            assert len(receiver) in VIOLAS_ADDRESS_LEN, f"{self.from_chain()} receiver({receiver}) is invalid"
    
    def stop(self):
        try:
            self.map_client.stop()
            self.from_client.stop()
            self.work_stop()
            pass
        except Exception as e:
            parse_except(e)

    def db_data_is_valid(self, data):
        try:
            toaddress   = data["receiver"]
            self._logger.debug(f"check address{toaddress}. len({toaddress}) in {VIOLAS_ADDRESS_LEN}?")
            return len(toaddress) in VIOLAS_ADDRESS_LEN
        except Exception as e:
            pass
        return False

    def reexchange_data_from_failed(self, gas = 1000):
        try:
            #get all excluded info from db
            rpcparams = {}
            ret = self.__get_reexchange()
            if(ret.state != error.SUCCEED):
                return ret
            rpcparams = ret.datas
            receivers = self.receivers

            #modulti receiver, one-by-one
            ret = self._pserver.get_latest_saved_ver()
            self.check_state_raise(ret, f"get_latest_saved_ver from request client failed.")
            latest_version = ret.datas
            self._logger.debug(f"get latest saved version from db is : {latest_version}")
            
            #get map sender from  senders
            ret = self.__get_map_sender_address()
            self.check_state_raise(ret, f"not found map sender{toaddress} or amount too low. check address and amount")
            map_sender = ret.datas
            self._logger.debug(f"map_sender({type(map_sender)}): {map_sender.address.hex()}")

            ret  = self.from_wallet.get_account(self.combine)
            self.check_state_raise(ret, f"get combin({self.combine})'s account failed.")
            combine_account = ret.datas

            for receiver in receivers:
                if not self.work() :
                    break
    
                ret = self.from_wallet.get_account(receiver)
                self.check_state_raise(ret, f"get receiver({receiver})'s account failed.")
                from_sender = ret.datas

                #get old transaction from db, check transaction. version and receiver is current value
                faileds = rpcparams.get(receiver)
                if faileds is not None:
                    self._logger.debug("start exchange failed datas from db. receiver={}".format(receiver))
                    for failed in faileds:
                        if (self.work() == False):
                            break

                        times = failed["times"]
                        state = localdb.state[failed["state"]]
                        detail = localdb.state[failed["detail"]]
                        if detail is not None:
                            detail = json.loads(detail)
                    
                        ret = self.pserver.get_tran_by_tranid(tran_id)
                        if ret.state != error.SUCCEED:
                            continue
                        data = ret.datas

                        if retry > 0 and retry >= times:
                            self.exec_refund(data, from_sender)
                            continue

                        ret = self.exec_exchange(data, from_sender, map_sender, combine_account, receiver, state = state, detail = detail)

            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret 

    def chain_data_is_valid(self, data):
        self._logger.debug(f"check address{data['to_address']}. len({data['to_address']}) in {VIOLAS_ADDRESS_LEN}?")
        if len(data["to_address"]) not in VIOLAS_ADDRESS_LEN:
            self._logger.warning(f"transaction(tran_id = {data["tran_id"]})) is invalid. ignore it and process next.")
            return False
        return True

    def has_info(self, tranid):
        ret = self._db.has_info(tranid)
        assert ret.state == error.SUCCEED, f"has_info({tranid}) failed."
        if ret.datas == True:
            self._logger.warning(f"found transaction(tran_id = {tran_id})) in db(maybe first run {self.dtype}). ignore it and process next.")
        return ret.datas

    def use_module(self, state, module_state):
        return state is None or state.value <= module_state.value

    def exec_refund(self, from_sender):
        amount      = int(data["amount"]) 
        tran_id     = data["tran_id"]
        stable_token_id = data["token_id"]
        payee = data["sender"]

        data = self.from_client.create_data_for_stop(self.from_chain, self.dtype, tran_id, 0) 
        ret = self.from_client.send_coin(from_sender, payee, amount, stable_token_id, data=data)
        if ret.state != error.SUCCEED:
            self.update_localdb_state_with_check(tran_id, localdb.state.SFAILED, "")
            return ret
        else:
            self.update_localdb_state_with_check(tran_id, localdb.state.SSUCCEED)


    def exec_exchange(self, data, from_sender, map_sender, combine_account, receiver, state = None, detail = {}):
        fromaddress = data["address"]
        amount      = int(data["amount"]) 
        sequence    = data["sequence"] 
        version     = data["version"]
        toaddress   = data["to_address"] #map token to
        tran_id     = data["tran_id"]
        out_amount  = data["out_amount"]
        times       = data["times"]
        opttype     = data["opttype"]
        stable_token_id = data["token_id"]
        from_token_id = stmanage.get_token_map(stable_token_id) #stable token -> LBRXXX token
        to_token_id    = self.to_token_id #token_id is map 

        ret = result(error.FAILED)
        self._logger.info(f"start exchange sender={fromaddress},  receiver={receiver}, sequence={sequence} " + \
                f"version={version}, toaddress={toaddress}, amount={amount}, tran_id={tran_id}, " + \
                f"from_token_id = {from_token_id} to_token_id={to_token_id} datas from server.")

        self._latest_version[receiver] = max(version, self._latest_version.get(receiver, -1))

        #if found transaction in history.db, then get_transactions's latest_version is error(too small or other case)'
        if state is None and self.has_info(tran_id):
            return ret

        if not self.chain_data_is_valid(data):
            return ret 

        #get swap before amount(to_token_id)
        
        if self.use_module(state, localdb.state.FAILED):
            ret = self.map_client.get_balance(combine_account.address.hex(), to_token_id)
            if ret.state != error.SUCCEED:
                self.insert_to_localdb_with_check(version, localdb.state.FAILED, tran_id, receiver)
                return ret
            before_amount = ret.balance
            detail.update({"before_amount": before_amount})

            #get gas for swap
            ret = self.map_client.swap_get_output_amount(from_token_id, to_token_id, amount)
            if ret.state != error.SUCCEED:
                self.insert_to_localdb_with_check(version, localdb.state.FAILED, tran_id, receiver)
            _, gas = ret.datas
            detail.update({"gas", gas})

            #swap LBRXXX -> VLSYYY
            ret = self.from_client.swap(map_sender, from_token_id, to_token_id, amount, out_amount, receiver = combine_account.address.hex(), gas_currency_code = from_token_id)
            if ret.state != error.SUCCEED:
                self.insert_to_localdb_with_check(version, localdb.state.FAILED, tran_id, receiver)
                return ret
            else:
                self.insert_to_localdb_with_check(version, localdb.state.SUCCEED, tran_id, receiver)

            #get swap after amount(to_token_id)
            ret = self.map_client.get_balance(combine_account.address.hex(), to_token_id)
            if ret.state != error.SUCCEED:
                ret = self.from_client.get_address_version(combine_account.address.hex())
                self.check_state_raise(ret, f"get_address_version({combine_account.address.hex})")
                detail.update({"swap_version": ret.datas})

                #if get balance, next execute, balance will change , so re swap, but combine token(to_token_id) is change, this time swap token_id should be burn
                self.update_localdb_state_with_check(tran_id, localdb.state.QBFAILED, json.dumps(detail)) #should get swap to_token balance from version
                return ret
            after_amount = ret.balance

            #clac diff balance
            diff_balance = after_amount - before_amount
            detail.update({"diff_balance": diff_balance})
        
        if self.use_module(state, localdb.state.QBFAILED):
            diff_balance = 1
            assert state != localdb.state.QBFAILED, "get swap token count from detail['swap_version'], here we think get_balance is always succeed"

        #mint LBRXXX to sender(type = LBRXXX), or check sender's token amount is enough
        if self.use_module(state, localdb.state.FILLFAILED):
            ret = self.__fill_address_token(map_sender.address.hex(), to_token_id, detail["diff_balance"], detail["gas"])
            if ret.state != error.SUCCEED:
                self.update_localdb_state_with_check(tran_id, localdb.state.FILLFAILED, json.dumps(detail))
                return ret

        #send libra token to payee address. P = payee
        if self.use_module(state, localdb.state.PFAILED):
            markdata = self.map_client.create_data_for_mark(self.map_chain, self.dtype, tran_id, version)
            ret = self.map_client.send_coin(combine_account, toaddress, detail["diff_balance"], to_token_id, data=markdata)
            if ret.state != error.SUCCEED:
                self.update_localdb_state_with_check(tran_id, localdb.state.PFAILED, json.dumps(detail))
                return ret
            else:
                self.update_localdb_state_with_check(tran_id, localdb.state.PSUCCEED)

        #send libra token to toaddress
        #sendexproofmark succeed , send violas coin with data for change tran state
        if self.use_module(state, localdb.state.VFAILED):
            self._send_coin_for_update_state_to_end(from_sender, receiver, tran_id, from_token_id)

    def start(self):
    
        try:
            self._logger.debug("start works")
            gas = 1000
            receivers = self.receivers

            #requirement checks
            self.__checks()
    
            #db state: VFAILED
            #send token is succeed, but change transaction state is failed, 
            ##so resend transaction to change state = end
            self._rechange_tran_state()

            #db state: FAILED
            #if history datas is found state = failed, exchange it until succeed
            self.reexchange_data_from_failed(gas)
    
            #db state: SUCCEED
            #check state from blockchain, and change exchange history data, 
            ##when change it to complete, can truncature history db
            self._rechange_db_state()

            #get map sender from senders
            ret = self.__get_map_sender_address()
            self.check_state_raise(ret, f"not found map sender{toaddress} or amount too low. check address and amount")
            map_sender = ret.datas
            self._logger.debug(f"map_sender({type(map_sender)}): {map_sender.address.hex()}")

            ret  = self.from_wallet.get_account(self.combine)
            self.check_state_raise(ret, f"get combin({self.combine})'s account failed.")
            combine_account = ret.datas

            #modulti receiver, one-by-one
            for receiver in receivers:
                if not self.work() :
                    break

                ret  = self.from_wallet.get_account(receiver)
                self.check_state_raise(ret, f"get receiver({receiver})'s account failed.")
                from_sender = ret.datas
                latest_version = self._latest_version.get(receiver, -1) + 1

                #get new transaction from server
                ret = self._pserver.get_transactions_for_start(receiver, self.dtype, latest_version)
                if ret.state == error.SUCCEED and len(ret.datas) > 0:
                    self._logger.debug("start exchange datas from violas server. receiver={}".format(receiver))
                    for data in ret.datas:
                        if not self.work() :
                            break
                        self.exec_exchange(data, from_sender, map_sender, combine_account, receiver)

                #get cancel transaction, this version not support
                #ret = self._pserver.get_transactions_for_start(receiver, self.dtype, latest_version)
                #if ret.state == error.SUCCEED and len(ret.datas) > 0:
                #    self._logger.debug("start exchange datas from violas server. receiver={}".format(receiver))
                #    for data in ret.datas:
                #        if not self.work() :
                #            break
                #        self.exec_refund(data, from_sender)
    
            ret = result(error.SUCCEED) 
    
        except Exception as e:
            ret = parse_except(e)
        finally:
            self._logger.debug("works end.")
    
        return ret
    
def main():
       print("start main")
       lv = exlv()
       
       ret = lv.start()
       if ret.state != error.SUCCEED:
           print(ret.message)

if __name__ == "__main__":
    main()
