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
class vlbase(baseobject):    
    def __init__(self, name, dtype, \
            fromnodes, mapnodes, \
            proofdb, receivers, senders, \
            swap_module, \
            fromchain, mapchain):
        ''' swap token and send coin to payee(metadata's to_address)
            fromnodes: swap source chain conf
            mapnodes : swap target chain conf
            proofdb  : transaction proof source
            receivers: receive swap chain' addresses
            senders  : sender target chain token adderss
            swap_module: violas chain swap module address
            fromchain: source chain name
            mapchain : target chain name
        '''

        baseobject.__init__(self, name)
        self.latest_version = {}
        self.from_chain = fromchain
        self.map_chain = mapchain
        self.append_property("from_client", violasproof(name, fromnodes, self.from_chain))
        self.append_property("map_client", violasproof(name, mapnodes, self.map_chain))
        self.append_property("db", localdb(name, f"{self.from_chain}_{self.name()}.db"))
        self.append_property("from_wallet", violaswallet(name, wallet_name, self.from_chain))
        self.append_property("map_wallet", violaswallet(name, wallet_name, self.map_chain))
    
        #violas/libra init
        self.append_property("pserver ", requestclient(name, proofdb))
        self.append_property("receivers", receivers)
        self.append_property("senders ", senders)
        self.append_property("dtype", dtype)
        self.append_property("to_token_id ", stmanage.get_type_stable_token(dtype))
        self.append_property("swap_module", swap_module)


        #use the above property, so call set_local_workspace here
        self.set_local_workspace()

    def __del__(self):
        pass

    def stop(self):
        try:
            self.map_client.stop()
            self.from_client.stop()
            self.work_stop()
            pass
        except Exception as e:
            parse_except(e)

    def set_local_workspace(self):
        self.append_property(f"{self.from_chain}_client", self.from_client)
        self.append_property(f"{self.map_chain}_client", self.map_client)
        self.append_property(f"{self.from_chain}_chain", self.from_chain)
        self.append_property(f"{self.map_chain}_chain", self.map_chain)
        self.append_property(f"{self.from_chain}_wallet", self.from_wallet)
        self.append_property(f"{self.map_chain}_wallet", self.map_wallet)
        self.violas_client.swap_set_module_address(self.swap_module)

    def insert_to_localdb_with_check(self, version, state, tran_id, receiver, detail = json.dumps({"default":"no-use"})):
        ret = self.db.insert_commit(version, state, tran_id, receiver, detail)
        assert (ret.state == error.SUCCEED), "db error"

    def update_localdb_state_with_check(self, tran_id, state, detail = json.dumps({"default":"no-use"})):
        ret = self.db.update_state_commit(tran_id, state, detail = detail)
        assert (ret.state == error.SUCCEED), "db error"

    def get_map_sender_address(self):
        try:
            sender_account = None
            for sender in self.senders:
                sender_account = self.map_wallet.get_account(sender)
                ret = result(error.SUCCEED, "", sender_account.datas)
                return ret

            return result(error.FAILED, "not found sender account")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def check_address_token_is_enough(self, client, address, token_id, amount):
        try:
            ret = client.get_balance(address, token_id = token_id)
            assert ret.state == SUCCEED, f"get balance failed"
            
            cur_amount = ret.datas
            return result(error.SUCCEED, datas = cur_amount >= amount)
        except Exception as e:
            ret = parse_except(e)
        return ret


    def merge_db_to_rpcparams(self, rpcparams, dbinfos):
        try:
            self._logger.debug("start merge_db_to_rpcparams")
            for info in dbinfos:
                new_data = {
                        "version":info.version, 
                        "tran_id":info.tranid, 
                        "state":info.state, 
                        "detail":info.detail,
                        "times":info.times}
                #server receiver address
                if info.receiver in rpcparams.keys():
                    rpcparams[info.receiver].append(new_data)
                else:
                    rpcparams[info.receiver] = [new_data]
    
            return result(error.SUCCEED, "", rpcparams)
        except Exception as e:
            ret = parse_except(e)
        return ret
    
    def load_record_and_merge(self, rpcparams, state, maxtimes = 999999999):
        try:
            ret = self.db.query_with_state(state, maxtimes)
            if(ret.state != error.SUCCEED):
                return ret 
    
            ret = self.merge_db_to_rpcparams(rpcparams, ret.datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_record_from_localdb_with_state(self, states):
        try:
            maxtimes = 5
            rpcparams = {}

            assert states is not None and len(states) > 0, f"args states is invalid."
            
            ## failed 
            if stmanage.get_max_times(self.name()) > 0:
                maxtimes = stmanage.get_max_times(self.name())

            for state in states:
                ret = self.load_record_and_merge(rpcparams, state)
                if(ret.state != error.SUCCEED):
                    return ret
            
            ret = result(error.SUCCEED, datas = rpcparams)
        except Exception as e:
            ret = parse_except(e)
        return ret

    # local db state is VSUCCEED , update state to COMPLETE
    def rechange_db_state(self, states):
        try:
            ##update violas blockchain state to end, if sendexproofmark is ok
            ret = self.get_record_from_localdb_with_state(states)
            if ret.state != error.SUCCEED:
                return ret
            rpcparams = ret.datas
            
            for key in rpcparams.keys():
                datas = ret.datas.get(key)
                for data in datas:
                    tran_id = data.get("tran_id")
                    if tran_id is None:
                        continue
                    ret = self.pserver.is_end(tran_id)
                    if ret.state == error.SUCCEED and ret.datas == True:
                       ret = self.update_localdb_state_with_check(tran_id, localdb.state.COMPLETE)

                    ret = self.pserver.is_stop(tran_id)
                    if ret.state == error.SUCCEED and ret.datas == True:
                       ret = self.update_localdb_state_with_check(tran_id, localdb.state.COMPLETE)

        except Exception as e:
            ret = parse_except(e)
        return ret

    def send_coin_for_update_state_to_end(self, sender, receiver, tran_id, token_id, amount = 1):
            self._logger.debug(f"start send_coin_for_update_state_to_end(sender={sender.address.hex()},"\
                    f"recever={receiver}, tran_id={tran_id}, amount={amount})")
            tran_data = self.from_client.create_data_for_end(self.from_chain, self.name(), tran_id, "")
            ret = self.from_client.send_coin(sender, receiver, amount, token_id, data = tran_data)
            if ret.state != error.SUCCEED:
                self.update_localdb_state_with_check(tran_id, localdb.state.VFAILED)
            else:
                self.update_localdb_state_with_check(tran_id, localdb.state.VSUCCEED)
            return ret

    def __checks(self):
        assert (len(self.senders) > 0), f"{self.map_chain} senders is invalid"
        for sender in self.senders:
            assert len(sender) in VIOLAS_ADDRESS_LEN, f"address({sender}) is invalied"

        assert (len(self.receivers) > 0), f"{self.from_chain} receivers is invalid."
        for receiver in self.receivers:
            assert len(receiver) in VIOLAS_ADDRESS_LEN, f"receiver({receiver}) is invalid"
    
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


    def chain_data_is_valid(self, data):
        if len(data["to_address"]) not in VIOLAS_ADDRESS_LEN:
            self._logger.warning(f"transaction(tran_id = {data['tran_id']})) is invalid. ignore it and process next.")
            return False
        return True

    def has_info(self, tranid):
        ret = self.db.has_info(tranid)
        assert ret.state == error.SUCCEED, f"has_info({tranid}) failed."
        if ret.datas == True:
            self._logger.warning(f"found transaction(tran_id = {tranid})) in db(maybe first run {self.dtype}). ignore it and process next.")
        return ret.datas

    def use_module(self, state, module_state):
        return state is None or state.value < module_state.value

    def exec_refund(self, data, from_sender):
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

    def reexchange_data_from_failed(self, states):
        try:
            #get all excluded info from db
            ret = self.get_record_from_localdb_with_state(states)
            if ret.state != error.SUCCEED:
                return ret
            rpcparams = ret.datas

            receivers = self.receivers

            #modulti receiver, one-by-one
            ret = self.pserver.get_latest_saved_ver()
            self.check_state_raise(ret, f"get_latest_saved_ver from request client failed.")
            latest_version = ret.datas
            self._logger.debug(f"get latest saved version from db is : {latest_version}")
            
            #get map sender from  senders
            ret = self.get_map_sender_address()
            self.check_state_raise(ret, f"not found map sender" + 
                    f"check address and amount")
            map_sender = ret.datas
            self._logger.debug(f"map_sender({type(map_sender)}): {map_sender.address.hex()}")

            combine_account = getattr(self, "combine_account", None)

            for receiver in receivers:
                if not self.work() :
                    break
    
                ret = self.from_wallet.get_account(receiver)
                self.check_state_raise(ret, f"get receiver({receiver})'s account failed.")
                from_sender = ret.datas

                #get old transaction from db, check transaction. 
                #version and receiver is current value
                faileds = rpcparams.get(receiver)
                if faileds is not None:
                    self._logger.debug(f"start exchange failed datas from db. receiver={receiver}")
                    for failed in faileds:
                        if (self.work() == False):
                            break

                        tran_id = failed["tran_id"]
                        times = failed["times"]
                        state = localdb.state(failed["state"])
                        detail = failed["detail"]
                        if detail is None or len(detail) == 0:
                            detail = {}
                        else:
                            detail = json.loads(failed["detail"])
                    
                        ret = self.pserver.get_tran_by_tranid(tran_id)
                        if ret.state != error.SUCCEED or ret.datas is None:
                            continue
        
                        data = ret.datas
                        retry = data.get("times")

                        #refund case: 
                        #   case 1: failed times check(metadata: times > 0 (0 = always))  
                        #   case 2: pre exec_refund is failed
                        if (retry != 0 and retry >= times) or state == localdb.state.SFAILED:
                            self.exec_refund(data, from_sender)
                            continue

                        ret = self.exec_exchange(data, from_sender, map_sender, \
                                combine_account, receiver, state = state, detail = detail)

            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret 

    def start(self):
    
        try:
            self._logger.debug("start works")
            gas = 1000
            receivers = self.receivers

            #requirement checks
            self.__checks()
    
            #db state: FAILED
            #if history datas is found state = failed, exchange it until succeed
            self.reexchange_data_from_failed(self.use_exec_failed_state)
    
            #db state: SUCCEED
            #check state from blockchain, and change exchange history data, 
            ##when change it to complete, can truncature history db
            self.rechange_db_state(self.use_exec_update_db_states)

            #get map sender from senders
            ret = self.get_map_sender_address()
            self.check_state_raise(ret, f"not found map sender. check address")
            map_sender = ret.datas
            self._logger.debug(f"map_sender({type(map_sender)}): {map_sender.address.hex()}")

            combine_account = self.combine_account

            #modulti receiver, one-by-one
            for receiver in receivers:
                if not self.work() :
                    break

                ret  = self.from_wallet.get_account(receiver)
                self.check_state_raise(ret, f"get receiver({receiver})'s account failed.")
                from_sender = ret.datas
                latest_version = self.latest_version.get(receiver, -1) + 1

                #get new transaction from server
                ret = self.pserver.get_transactions_for_start(receiver, self.dtype, latest_version)
                if ret.state == error.SUCCEED and len(ret.datas) > 0:
                    self._logger.debug(f"start exchange datas from violas server.receiver={receiver}")
                    for data in ret.datas:
                        if not self.work() :
                            break
                        self.exec_exchange(data, from_sender, map_sender, combine_account, receiver)

                #get cancel transaction, this version not support
                ret = self.pserver.get_transactions_for_cancel(receiver, self.dtype, latest_version)
                if ret.state == error.SUCCEED and len(ret.datas) > 0:
                    self._logger.debug("start exchange datas from violas server.receiver={receiver}")
                    for data in ret.datas:
                        if not self.work() :
                            break
                        self.exec_refund(data, from_sender)
    
            ret = result(error.SUCCEED) 
    
        except Exception as e:
            ret = parse_except(e)
        finally:
            self._logger.debug("works end.")
    
        return ret
    
def main():
       print("start main")

if __name__ == "__main__":
    main()
