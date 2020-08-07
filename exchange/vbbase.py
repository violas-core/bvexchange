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
from comm.amountconver import amountconver
from db.dblocal import dblocal as localdb
import vlsopt.violasclient
from vlsopt.violasclient import violasclient, violaswallet, violasserver
from btc.btcclient import btcclient
from btc.btcwallet import btcwallet
from vlsopt.violasproof import violasproof
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from baseobject import baseobject
from enum import Enum
from vrequest.request_client import requestclient

#module self.name
#name="vbbase"
wallet_name = "vwallet"

VIOLAS_ADDRESS_LEN = comm.values.VIOLAS_ADDRESS_LEN
#load logging
class vbbase(baseobject):    

    class amountswap(amountconver):
        pass

    def __init__(self, name, dtype, \
            btcnodes, violasnodes, \
            proofdb, receivers, senders, \
            swap_module, \
            swap_owner, \
            fromchain, \
            mapchain):
        ''' swap token and send coin to payee(metadata's to_address)
            fromnodes: swap source chain conf
            mapnodes : swap target chain conf
            proofdb  : transaction proof source
            receivers: receive swap chain' addresses
            senders  : sender target chain token adderss
            swap_module: violas chain swap module address
            swap_owner: violas chain swap owner address
            fromchain: source chain name
            mapchain : target chain name
        '''

        baseobject.__init__(self, name)
        self.latest_version = {}
        self.from_chain = fromchain
        self.map_chain = mapchain
        self.append_property("btc_client", btcclient(name, btcnodes))
        self.append_property("violas_client", violasproof(name, violasnodes, "violas"))
        self.append_property("db", localdb(name, f"{self.from_chain}_{self.name()}.db"))
    
        #violas/libra init
        self.append_property("receivers", receivers)
        self.append_property("senders ", senders)
        self.append_property("dtype", dtype)
        self.append_property("to_token_id ", stmanage.get_type_stable_token(dtype))
        self.append_property("swap_module", swap_module)
        self.append_property("swap_owner", swap_owner)
        self.append_property("proofdb", proofdb)

        #use the above property, so call set_local_workspace here
        self.set_local_workspace()

    def __del__(self):
        pass

    def stop(self):
        try:
            self.violas_client.stop()
            self.btc_client.stop()
            self.work_stop()
            pass
        except Exception as e:
            parse_except(e)

    def set_local_workspace(self):
        setattr(self, "excluded", [])
        self.append_property(f"{self.from_chain}_chain", self.from_chain)
        self.append_property(f"{self.map_chain}_chain", self.map_chain)
        self.violas_client.swap_set_module_address(self.swap_module)
        self.violas_client.swap_set_owner_address(self.swap_owner)
        if self.from_chain == "btc":
            self.append_property("pserver", self.btc_client)
            self.append_property("from_wallet", btcwallet(self.name(), None))
            self.append_property("from_client", self.btc_client)
            self.append_property("btc_wallet", self.from_wallet)
        else:
            self.append_property("pserver", requestclient(self.name(), self.proofdb))
            self.append_property("from_wallet", violaswallet(self.name(), wallet_name, self.from_chain))
            self.append_property("from_client", self.violas_client)
            self.append_property("violas_wallet", self.from_wallet)

        if self.map_chain == "btc":
            self.append_property("map_wallet", btcwallet(self.name(), None))
        else:
            self.append_property("map_wallet", violaswallet(self.name(), wallet_name, self.map_chain))

    def insert_to_localdb_with_check(self, version, state, tran_id, receiver, detail = json.dumps({"default":"no-use"})):
        ret = self.db.insert_commit(version, state, tran_id, receiver, detail)
        assert (ret.state == error.SUCCEED), "db error"

    def update_localdb_state_with_check(self, tran_id, state, detail = json.dumps({"default":"no-use"})):
        ret = self.db.update_state_commit(tran_id, state, detail = detail)
        assert (ret.state == error.SUCCEED), "db error"

    #overwrite
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

    def show_load_record_info(self, rpcparams):
        infos = {}
        for key, values in rpcparams.items():
            for value in values:
                info_key = f"{localdb.state(value.get('state')).name}"
                if info_key not in infos:
                    infos.update({info_key : 1})
                else:
                    infos[info_key] = infos[info_key] + 1
        self._logger.debug(f"record info:{infos}")


    def get_record_from_localdb_with_state(self, states):
        try:
            maxtimes = 999999999
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

    def is_end(self, tran_id):
        return self.pserver.is_end(tran_id)

    def is_stop(self, tran_id):
        return self.pserver.is_stop(tran_id)

    # local db state is VSUCCEED , update state to COMPLETE
    def rechange_db_state(self, states):
        try:
            ##update violas blockchain state to end, if sendexproofmark is ok
            self._logger.debug(f"start rechange_db_state({[state.name for state in states]})")
            ret = self.get_record_from_localdb_with_state(states)
            if ret.state != error.SUCCEED:
                return ret
            rpcparams = ret.datas
            self.show_load_record_info(rpcparams)
            
            for key in rpcparams.keys():
                datas = ret.datas.get(key)
                for data in datas:
                    tran_id = data.get("tran_id")
                    if tran_id is None:
                        continue
                    ret = self.is_end(tran_id)
                    if ret.state == error.SUCCEED and ret.datas == True:
                       ret = self.update_localdb_state_with_check(tran_id, localdb.state.COMPLETE)

                    ret = self.is_stop(tran_id)
                    if ret.state == error.SUCCEED and ret.datas == True:
                       ret = self.update_localdb_state_with_check(tran_id, localdb.state.COMPLETE)

        except Exception as e:
            ret = parse_except(e)
        return ret

    def send_coin_for_update_state_to_end(self, sender, receiver, tran_id, token_id, amount = 1, **kwargs):
            self._logger.debug(f"start send_coin_for_update_state_to_end(sender={sender},"\
                    f"recever={receiver}, tran_id={tran_id}, amount={amount})")
            tran_data = self.from_client.create_data_for_end(self.from_chain, self.dtype, tran_id, **kwargs)
            ret = self.from_client.send_coin(sender, receiver, amount, token_id, data = tran_data)
            if ret.state != error.SUCCEED:
                self.update_localdb_state_with_check(tran_id, localdb.state.VFAILED)
            else:
                self.update_localdb_state_with_check(tran_id, localdb.state.VSUCCEED)
            return ret

    def __checks(self):
        return True
    
    def db_data_is_valid(self, data):
        try:
            toaddress   = data["receiver"]
            self._logger.debug(f"check address{toaddress}. len({toaddress}) in {VIOLAS_ADDRESS_LEN}?")
        except Exception as e:
            pass
        return False


    def chain_data_is_valid(self, data):
        if False: # btc and violas is diff ????????
            self._logger.warning(f"transaction(tran_id = {data['tran_id']})) is invalid. " + 
                    f"ignore it and process next.")
            return False
        return True

    def has_info(self, tranid):
        ret = self.db.has_info(tranid)
        assert ret.state == error.SUCCEED, f"has_info({tranid}) failed."
        if ret.datas == True:
            self._logger.warning(f"found transaction(tran_id = {tranid})) in db(maybe first run {self.dtype}). " + 
                    f"ignore it and process next.")
        return ret.datas

    def use_module(self, state, module_state):
        return state is None or state.value < module_state.value

    def is_target_state(self, tranid, state):
        ret = self.db.is_target_state(tranid, state)
        assert ret.state == error.SUCCEED, f"is_target_state({tranid}, {state}) failed."
        return ret.datas

    def exec_refund(self, data, from_sender):
        amount          = int(data["amount"]) 
        tran_id         = data["tran_id"]
        stable_token_id = data["token_id"]
        payee           = data["address"]

        if self.is_target_state(tran_id, localdb.state.SSUCCEED.value):
            self._logger.warning(f"found transaction is stopped. (tran_id = {tran_id})) in db({self.dtype}). not exec_refund, ignore it and process next.")
            return result(error.SUCCEED)
        ##convert to BTC satoshi(100000000satoshi == 1000000vBTC)
        ##libra or violas not convert
        amount = self.amountswap(amount, self.amountswap.amounttype[self.from_chain.upper()]).amount(self.from_chain)

        self._logger.debug(f"execute refund({tran_id}, {amount}, {stable_token_id})")
        data = self.from_client.create_data_for_stop(self.from_chain, self.dtype, tran_id, 0) 
        ret = self.from_client.send_coin(from_sender, payee, amount, stable_token_id, data=data)
        if ret.state != error.SUCCEED:
            self.update_localdb_state_with_check(tran_id, localdb.state.SFAILED)
            return ret
        else:
            self.update_localdb_state_with_check(tran_id, localdb.state.SSUCCEED)
        return result(error.SUCCEED)

    def reexchange_data_from_failed(self, states):
        try:
            #get all info from db
            self._logger.debug(f"start re exchange failed transaction({[state.name for state in states]})")
            ret = self.get_record_from_localdb_with_state(states)
            if ret.state != error.SUCCEED:
                return ret
            rpcparams = ret.datas
            self.show_load_record_info(rpcparams)

            receivers = self.receivers

            #get map sender from  senders
            ret = self.get_map_sender_address()
            self.check_state_raise(ret, f"not found map sender" + 
                    f"check address and amount")
            map_sender = ret.datas

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
                        times   = failed["times"]
                        state   = localdb.state(failed["state"])
                        detail  = failed["detail"]
                        if detail is None or len(detail) == 0:
                            detail = {}
                        else:
                            detail = json.loads(failed["detail"])
                    
                        ret = self.pserver.get_tran_by_tranid(tran_id)
                        if ret.state != error.SUCCEED or ret.datas is None:
                            self._logger.error(f"get transaction(tran_id = {tran_id}) failed.")
                            continue
        
                        data = ret.datas
                        retry = data.get("times")

                        #refund case: 
                        #   case 1: failed times check(metadata: times > 0 (0 = always))  
                        #   case 2: pre exec_refund is failed
                        if (retry != 0 and retry <= times) or state == localdb.state.SFAILED:
                            ret = self.exec_refund(data, from_sender)
                            if ret.state != error.SUCCEED:
                                self._logger.error(ret.message)
                            continue

                        ret = self.exec_exchange(data, from_sender, map_sender, \
                                combine_account, receiver, state = state, detail = detail)
                        if ret.state != error.SUCCEED:
                            self._logger.error(ret.message)

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
            self._logger.debug(f"************************************************************ 1/4")
            self.reexchange_data_from_failed(self.use_exec_failed_state)
    
            #db state: SUCCEED
            #check state from blockchain, and change exchange history data, 
            ##when change it to complete, can truncature history db
            self._logger.debug(f"************************************************************ 2/4")
            self.rechange_db_state(self.use_exec_update_db_states)

            #get map sender from senders
            ret = self.get_map_sender_address()
            self.check_state_raise(ret, f"not found map sender. check address")
            map_sender = ret.datas

            combine_account = self.combine_account

            #modulti receiver, one-by-one
            self._logger.debug(f"************************************************************ 3/4")
            for receiver in receivers:
                if not self.work() :
                    break

                ret  = self.from_wallet.get_account(receiver)
                self.check_state_raise(ret, f"get receiver({receiver})'s account failed.")
                from_sender = ret.datas
                latest_version = self.latest_version.get(receiver, -1) + 1

                #get new transaction from server
                self._logger.debug(f"start exchange(data type: start), datas from violas server.receiver={receiver}")
                ret = self.pserver.get_transactions_for_start(receiver, self.dtype, latest_version, excluded = self.excluded)
                self._logger.debug(f"will execute transaction(start) : {len(ret.datas)}")
                if ret.state == error.SUCCEED and len(ret.datas) > 0:
                    for data in ret.datas:
                        if not self.work() :
                            break
                        ret = self.exec_exchange(data, from_sender, map_sender, combine_account, receiver)
                        if ret.state != error.SUCCEED:
                            self._logger.error(ret.message)

                #get cancel transaction, this version not support
                self._logger.debug(f"start exchange(data type: cancel), datas from violas server.receiver={receiver}")
                ret = self.pserver.get_transactions_for_cancel(receiver, self.dtype, 0, excluded = None)
                self._logger.debug(f"will execute transaction(cancel) count: {len(ret.datas)}")
                if ret.state == error.SUCCEED and len(ret.datas) > 0:
                    for data in ret.datas:
                        if not self.work() :
                            break
                        ret = self.exec_refund(data, from_sender)
                        if ret.state != error.SUCCEED:
                            self._logger.error(ret.message)
    
            ret = result(error.SUCCEED) 
            self._logger.debug(f"************************************************************ 4/4")
    
        except Exception as e:
            ret = parse_except(e)
        finally:
            self._logger.debug("works end.")
    
        return ret
    
def main():
       print("start main")

if __name__ == "__main__":
    main()
