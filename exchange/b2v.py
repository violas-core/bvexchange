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
from baseobject import baseobject
from enum import Enum
from vrequest.request_client import requestclient
from exchange.vbbase import vbbase

#module self.name
#name="exlv"
wallet_name = "vwallet"

VIOLAS_ADDRESS_LEN = comm.values.VIOLAS_ADDRESS_LEN
#load logging
class b2v(vbbase):    
    def __init__(self, name, 
            dtype, 
            btcnodes, 
            vlsnodes, 
            proofdb, 
            receivers, 
            senders, 
            swap_module):

        vbbase.__init__(self, name, dtype, btcnodes, vlsnodes, \
                proofdb, receivers, senders, swap_module, \
                "btc", "violas")
        self.init_extend_property()
        self.init_exec_states()

    def __del__(self):
        pass

    def init_extend_property(self):
        self.append_property("combine_account", None)

    def init_exec_states(self):

        self.append_property("use_exec_update_db_states", 
                [localdb.state.VSUCCEED, localdb.state.SSUCCEED])

        self.append_property("use_exec_failed_state", 
            [state for state in localdb.state \
                    if state not in [localdb.state.COMPLETE, \
                        localdb.state.VSUCCEED, \
                        localdb.state.SSUCCEED]])

        excluded_states = [localdb.state.VFAILED, localdb.state.PFAILED]
        ret = self.get_record_from_localdb_with_state(excluded_states)
        if ret.state != error.SUCCEED:
            return ret
        setattr(self, "excluded", ret.datas)

    def fill_address_token(self, address, token_id, amount, gas=40_000):
        try:
            ret = self.btc_client.get_balance(address, token_id = token_id)
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

        swap_amount = self.amountswap(amount, self.amountswap.amounttype.BTC)
        amount = swap_amount.violas_amount

        ret = result(error.FAILED)
        self._logger.info(f"start exchange b2v.sender={fromaddress},  receiver={receiver}, " + \
            f"sequence={sequence}, version={version}, toaddress={toaddress}, amount={amount}, " + \
            f"tran_id={tran_id}, from_token_id = {from_token_id}, to_token_id={to_token_id} " + \
            f"map_token_id = {map_token_id}, state = {state}, detail = {detail} datas from server.")

        if state is not None:
            self._latest_version[receiver] = max(version, self._latest_version.get(receiver, -1))

        #if found transaction in history.db, then get_transactions's latest_version is error(too small or other case)'
        if state is None and self.has_info(tran_id):
            return ret

        if self.use_module(state, localdb.state.START):
            self.insert_to_localdb_with_check(version, localdb.state.START, tran_id, receiver)

        if self.use_module(state, localdb.state.PSUCCEED) or \
                self.use_module(state, localdb.state.ESUCCEED) or \
                self.use_module(state, localdb.state.FILLSUCCEED):
            #get output and gas
            ret = self.violas_client.swap_get_output_amount(map_token_id, to_token_id, amount)
            if ret.state != error.SUCCEED:
                self.update_localdb_state_with_check(tran_id, localdb.state.FAILED, receiver)
                return ret
            else:
                self.update_localdb_state_with_check(tran_id, localdb.state.ESUCCEED, receiver)

            out_amount_chian, gas = ret.datas
            #temp value(test)
            if out_amount <= 0:
                out_amount = out_amount_chian
            elif out_amount > out_amount_chian: #don't execute swap, Reduce the cost of the budget
                self.update_localdb_state_with_check(tran_id, localdb.state.FAILED, receiver)
                return ret
            detail.update({"gas": gas})

            #fill BTCXXX to sender(type = LBRXXX), or check sender's token amount is enough
            ret = self.fill_address_token(map_sender, map_token_id, amount, detail["gas"])
            if ret.state != error.SUCCEED:
                self.update_localdb_state_with_check(tran_id, localdb.state.FILLFAILED, \
                      json.dumps(detail))
                return ret
            else:
                self.update_localdb_state_with_check(tran_id, localdb.state.FILLSUCCEED, \
                      json.dumps(detail))

            #swap LBRXXX -> VLSYYY and send VLSXXX to toaddress(client payee address)
            ret = self.violas_client.swap(map_sender, map_token_id, to_token_id, amount, \
                    out_amount, receiver = toaddress, gas_currency_code = map_token_id)
            if ret.state != error.SUCCEED:
                self.update_localdb_state_with_check(tran_id, localdb.state.PFAILED, json.dumps(detail))
                return ret
            else:
                self.update_localdb_state_with_check(tran_id, localdb.state.PSUCCEED, json.dumps(detail))

            version = self.violas_client.get_address_version(map_sender).datas
        
        #send libra token to toaddress
        #sendexproofmark succeed , send violas coin with data for change tran state
        if self.use_module(state, localdb.state.VSUCCEED):
            self.send_coin_for_update_state_to_end(from_sender, receiver, tran_id, \
                    from_token_id, amount = 0, version = version)

def main():
       print("start main")
       stmanage.set_conf_env("../bvexchange.toml")
       dtype = "b2vusd"
       obj = b2v(dtype, 
               dtype,
               stmanage.get_btc_nodes(), 
               stmanage.get_violas_nodes(),
               stmanage.get_db(dtype), 
               list(set(stmanage.get_receiver_address_list(dtype, "btc", False))),
               list(set(stmanage.get_sender_address_list(dtype, "violas", False))),
               stmanage.get_swap_module()
               )
       ret = obj.start()
       if ret.state != error.SUCCEED:
           print(ret.message)

if __name__ == "__main__":
    main()
