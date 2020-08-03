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
from db.dblocal import dblocal as localdb
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
            combine, #btc address
            swap_module,
            swap_owner):

        '''bitcoin BTC swap to violas stable token 
            @dtype : opttype
            @btcnodes: btc node configure
            @vlsnodes: violas nodes configure
            @proofdb: violas proof configure, no-use
            @receivers: btc address, get valid swap transaction
            @senders: violas senders address, use this address to transfer(diff chain)
            @combine: btc address, change state transaction's payer
            @swap_module: swap module address
            @swap_owner: swap owner address
        '''
        vbbase.__init__(self, name, dtype, btcnodes, vlsnodes, \
                proofdb, receivers, senders, swap_module, swap_owner,\
                "btc", "violas")
        self.append_property("combine_account", combine)
        self.init_extend_property()
        self.init_exec_states()

    def __del__(self):
        pass

    def init_extend_property(self):
        pass

    def init_exec_states(self):

        self.append_property("use_exec_update_db_states", 
                [localdb.state.VSUCCEED, localdb.state.SSUCCEED])

        self.append_property("use_exec_failed_state", 
            [state for state in localdb.state \
                    if state not in [localdb.state.COMPLETE, \
                        localdb.state.VSUCCEED, \
                        localdb.state.SSUCCEED]])

        
        ret = self.get_record_from_localdb_with_state(self.use_exec_failed_state)
        if ret.state != error.SUCCEED:
            return ret
        excluded = []
        for receiver, datas in ret.datas.items():
            for data in datas:
                address_seq = data.get("tran_id").split("_")
                excluded.append({"address":address_seq[0], "sequence":address_seq[1]})

        setattr(self, "excluded", excluded)

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
        ''' execute exchange 
            @data : proof datas
            @from_sender: 
            @map_sender:
            @combine_account: inner 
            @receiver: swap transaction's server address
            @state: check is new exchange or re-execute exchange with it, 
                    None is new, other is re-execute
            detail: when state is not None , get some info from detail
        '''
        fromaddress = data["address"]
        amount      = int(data["amount"]) #here is btc amount
        sequence    = data["sequence"] 
        version     = data["version"]
        toaddress   = data["to_address"] #map token to
        tran_id     = data["tran_id"]
        out_amount  = data["out_amount"]
        times       = data["times"]
        opttype     = data["opttype"]
        stable_token_id = data["token_id"]
        from_token_id = stable_token_id
        assert from_token_id is not None, f"stable_token_id is None."
        map_token_id = stmanage.get_token_map(stable_token_id) #stable token -> LBRXXX token
        to_token_id    = self.to_token_id #token_id is map 

        swap_amount = self.amountswap(amount, self.amountswap.amounttype.VIOLAS) #btcclient has / 100
        amount = swap_amount.violas_amount

        self._logger.info(f"exec_exchange-start. start exec_exchange . tran_id={tran_id}, state = {state}.")

        #if found transaction in history.db, then get_transactions's latest_version is error(too small or other case)'
        if state is None and self.has_info(tran_id):
            return result(error.SUCCEED)

        if self.use_module(state, localdb.state.START):
            self.insert_to_localdb_with_check(version, localdb.state.START, tran_id, receiver)

        if self.use_module(state, localdb.state.PSUCCEED) or \
                self.use_module(state, localdb.state.ESUCCEED) or \
                self.use_module(state, localdb.state.FILLSUCCEED):
            #get output and gas
            self._logger.debug(f"exec_exchange-1. start swap_get_output_amount({map_token_id} {to_token_id} {amount})...")
            ret = self.violas_client.swap_get_output_amount(map_token_id, to_token_id, amount)
            if ret.state != error.SUCCEED:
                self.update_localdb_state_with_check(tran_id, localdb.state.FAILED)
                return ret
            else:
                self.update_localdb_state_with_check(tran_id, localdb.state.ESUCCEED)
            out_amount_chian, gas = ret.datas
            self._logger.debug(f"exec_exchange-1.result : out_amount = {out_amount_chian} gas = {gas}")

            #temp value(test)
            if out_amount <= 0:
                out_amount = out_amount_chian
            elif out_amount > out_amount_chian: #don't execute swap, Reduce the cost of the budget
                self.update_localdb_state_with_check(tran_id, localdb.state.FAILED)
                return result(error.FAILED, \
                            f"don't execute swap(out_amount({out_amount}) > cur_outamount({out_amount_chian})), Reduce the cost of the budget")
            detail.update({"gas": gas})

            #fill BTCXXX to sender(type = LBRXXX), or check sender's token amount is enough
            self._logger.debug("exec_exchange-2. start fill_address_token...")
            ret = self.fill_address_token(map_sender.address.hex(), map_token_id, amount, detail["gas"])
            if ret.state != error.SUCCEED:
                self.update_localdb_state_with_check(tran_id, localdb.state.FILLFAILED, \
                      json.dumps(detail))
                self._logger.debug("exec_exchange-2.result: failed.")
                return ret
            else:
                self.update_localdb_state_with_check(tran_id, localdb.state.FILLSUCCEED, \
                      json.dumps(detail))

            #swap LBRXXX -> VLSYYY and send VLSXXX to toaddress(client payee address)
            self._logger.debug("exec_exchange-3. start swap...")
            ret = self.violas_client.swap(map_sender, map_token_id, to_token_id, amount, \
                    out_amount, receiver = toaddress, gas_currency_code = map_token_id)
            if ret.state != error.SUCCEED:
                self.update_localdb_state_with_check(tran_id, localdb.state.PFAILED, json.dumps(detail))
                self._logger.debug("exec_exchange-3.result: failed.")
                return ret
            else:
                self.update_localdb_state_with_check(tran_id, localdb.state.PSUCCEED, json.dumps(detail))

            self._logger.debug("exec_exchange-4. start get_address_version...")
            version = self.violas_client.get_address_version(map_sender.address.hex()).datas
            self._logger.debug(f"exec_exchange-4.result: version = {version}")
        
        #send libra token to toaddress
        #sendexproofmark succeed , send violas coin with data for change tran state
        if self.use_module(state, localdb.state.VSUCCEED):
            self._logger.debug("exec_exchange-5. start send_coin_for_update_state_to_end...")
            ret = self.send_coin_for_update_state_to_end(from_sender, self.combine_account, tran_id, \
                    from_token_id, amount = 0, version = version)
            if ret.state != error.SUCCEED:
                return ret

        self._logger.debug("exec_exchange-end.")
        return result(error.SUCCEED)

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
               stmanage.get_combine_address(dtype, "btc", True),
               stmanage.get_swap_module(),
               stmanage.get_swap_owner()
               )
       ret = obj.start()
       if ret.state != error.SUCCEED:
           print(ret.message)

if __name__ == "__main__":
    main()
