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
    def __init__(self, name, dtype, vlsnodes, lbrnodes, proofdb, receivers, senders,  fromchain, mapchain):
        baseobject.__init__(self, name)
        self._latest_version = {}
        self.from_chain = fromchain
        self.map_chain = mapchain
        self._from_client = violasproof(name, vlsnodes, self.from_chain)
        self._map_client = violasproof(name, mapnodes, mapchain)
        self._db = localdb(name, f"{self.from_chain}_{self.name()}.db")
        self._fromwallet = violaswallet(name, wallet_name, self.from_chain)
        self._mapwallet = violaswallet(name, wallet_name, self.map_chain)
    
        #violas/libra init
        self._pserver = requestclient(name, proofdb)
        self._receivers = receivers
        self._senders = senders
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

    def fill_address_token(self, client, address, token_id, amount, gas=40_000):
        try:
            ret = client.get_balance(address, token_id = token_id)
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
                        "version":info.version, "tran_id":info.tranid, "state":info.state, "detail":info.detail}
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

    #should overwrite
    def get_reset_history_state_to_complete(self):
        try:
            maxtimes = 5
            rpcparams = {}
            
            ## failed 
            if stmanage.get_max_times(self.name()) > 0:
                maxtimes = stmanage.get_max_times(self.name())

            ret = self.__load_record_and_merge(rpcparams, localdb.state.VSUCCEED)
            if(ret.state != error.SUCCEED):
                return ret
            
            ret = result(error.SUCCEED, "", rpcparams)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def _rechange_db_state(self):
        try:
            ##update violas blockchain state to end, if sendexproofmark is ok
            ret = self.get_reset_history_state_to_complete()
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


def main():
       print("start main")
       lv = exlv()
       
       ret = lv.start()
       if ret.state != error.SUCCEED:
           print(ret.message)

if __name__ == "__main__":
    main()
