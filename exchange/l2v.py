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
from db.dbl2v import dbl2v as localdb
import vlsopt.violasclient
from vlsopt.violasclient import violasclient, violaswallet, violasserver
from vlsopt.violasproof import violasproof
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from baseobject import baseobject
from enum import Enum
from vrequest.request_client import requestclient
from exchange.vlbase import vlbase

#module self.name
#name="exlv"
wallet_name = "vwallet"

VIOLAS_ADDRESS_LEN = comm.values.VIOLAS_ADDRESS_LEN
#load logging
class l2v(vlbase):    
    def __init__(self, name, 
            dtype, 
            vlsnodes, 
            lbrnodes, 
            proofdb, 
            receivers, 
            senders, 
            swap_module):

        vlbase.__init__(self, name, dtype, lbrnodes, vlsnodes, \
                proofdb, receivers, senders, swap_module, \
                "libra", "violas")
        self.init_extend_property()
        self.init_exec_states()

    def __del__(self):
        pass

    def init_extend_property(self):
        self.append_property("combine_account", None)

    def init_exec_states(self):
        use_exec_failed_state = []
        use_exec_failed_state.append(localdb.state.FAILED)
        use_exec_failed_state.append(localdb.state.FILLFAILED)
        use_exec_failed_state.append(localdb.state.PFAILED)
        use_exec_failed_state.append(localdb.state.VFAILED)
        use_exec_failed_state.append(localdb.state.SFAILED)
        self.append_property("use_exec_failed_state", 
                use_exec_failed_state)

        use_exec_update_db_states = []
        use_exec_update_db_states.append(localdb.state.VSUCCEED)
        use_exec_update_db_states.append(localdb.state.SSUCCEED)
        self.append_property("use_exec_update_db_states", 
                use_exec_update_db_states)

    def fill_address_token(self, address, token_id, amount, gas=40_000):
        try:
            ret = self.violas_client.get_balance(address, token_id = token_id)
            assert ret.state == error.SUCCEED, f"get balance failed"
            
            cur_amount = ret.datas
            if cur_amount < amount + gas:
                ret = self.violas_client.mint_coin(address, \
                        amount = amount + gas - cur_amount, \
                        token_id = token_id)
                return ret

            return result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def exec_exchange(self, data, from_sender, map_sender, combine_account, receiver, \
            state = None, detail = {}):
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
        from_token_id = stable_token_id
        map_token_id = stmanage.get_token_map(stable_token_id) #stable token -> LBRXXX token
        to_token_id    = self.to_token_id #token_id is map 

        ret = result(error.FAILED)
        self._logger.info(f"start exchange l2v.sender={fromaddress},  receiver={receiver}, " + \
            f"sequence={sequence}, version={version}, toaddress={toaddress}, amount={amount}, " + \
            f"tran_id={tran_id}, from_token_id = {from_token_id}, to_token_id={to_token_id} " + \
            f"map_token_id = {map_token_id}, state = {state}, detail = {detail} datas from server.")

        if state is not None:
            self._latest_version[receiver] = max(version, self._latest_version.get(receiver, -1))

        #if found transaction in history.db, then get_transactions's latest_version is error(too small or other case)'

        if not self.chain_data_is_valid(data):
           return 

        if self.use_module(state, localdb.state.START):
            self.insert_to_localdb_with_check(version, localdb.state.START, tran_id, receiver)

        if self.use_module(state, localdb.state.FAILED):
            ret = self.violas_client.swap_get_output_amount(map_token_id, to_token_id, amount)
            if ret.state != error.SUCCEED:
                self.update_localdb_state_with_check(tran_id, localdb.state.FAILED, receiver)
                return ret

            out_amount_chian, gas = ret.datas
            #temp value(test)
            if out_amount <= 0:
                out_amount = out_amount_chian
            detail.update({"gas": gas})

        if self.use_module(state, localdb.state.FILLFAILED):
            #mint LBRXXX to sender(type = LBRXXX), or check sender's token amount is enough
            ret = self.fill_address_token(map_sender.address.hex(), map_token_id, amount, detail["gas"])
            if ret.state != error.SUCCEED:
                self.update_localdb_state_with_check(tran_id, localdb.state.FILLFAILED, \
                      json.dumps(detail))
                return ret

        if self.use_module(state, localdb.state.PFAILED):
            #swap LBRXXX -> VLSYYY and send VLSXXX to toaddress(client payee address)
            ret = self.violas_client.swap(map_sender, map_token_id, to_token_id, amount, \
                    out_amount, receiver = toaddress, gas_currency_code = map_token_id)
            if ret.state != error.SUCCEED:
                self.insert_to_localdb_with_check(version, localdb.state.PFAILED, tran_id, receiver)
                return ret
        
        #send libra token to toaddress
        #sendexproofmark succeed , send violas coin with data for change tran state
        if self.use_module(state, localdb.state.VFAILED):
            self.send_coin_for_update_state_to_end(from_sender, receiver, tran_id, from_token_id)

def main():
       print("start main")
       stmanage.set_conf_env("../bvexchange.toml")
       mod = "l2v"
       dtype = "l2vusd"
       obj = l2v(mod, 
               dtype,
               stmanage.get_violas_nodes(), 
               stmanage.get_libra_nodes(),
               stmanage.get_db(dtype), 
               list(set(stmanage.get_receiver_address_list(dtype, "libra", False))),
               list(set(stmanage.get_sender_address_list(dtype, "violas", False))),
               stmanage.get_swap_module()
               )
       ret = obj.start()
       if ret.state != error.SUCCEED:
           print(ret.message)

if __name__ == "__main__":
    main()
