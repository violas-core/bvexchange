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
from enum import Enum
from exchange.vlbase import vlbase

#module self.name
#name="exlv"
wallet_name = "vwallet"

VIOLAS_ADDRESS_LEN = comm.values.VIOLAS_ADDRESS_LEN
#load logging
class vlmap(vlbase):    
    def __init__(self, name, 
            dtype, 
            fromnodes, 
            mapnodes, 
            proofdb, 
            receivers, 
            senders, 
            fromchain,
            mapchain
            ):

        vlbase.__init__(self, name, dtype, fromnodes, mapnodes, \
                proofdb, receivers, senders, None, None, \
                fromchain, mapchain)
        self.init_extend_property()
        self.init_exec_states()
        self.init_fill_address_token_violas()

    def __del__(self):
        pass
    
    @property
    def fill_address_token(self):
        return self._fill_address_token

    def init_fill_address_token_violas(self):
        self.fill_address_token = {}
        self.fill_address_token.update({"violas": self.init_fill_address_token_violas})
        self.fill_address_token.update({"libra": self.init_fill_address_token_libra})


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

    def fill_address_token_violas(self, address, token_id, amount, gas=40_000):
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

    def fill_address_token_libra(self, address, token_id, amount, gas=40_000):
        try:
            ret = self.libra_client.get_balance(address, token_id = token_id)
            assert ret.state == error.SUCCEED, f"get balance failed"
            
            cur_amount = ret.datas
            if cur_amount < amount + gas:
                return result(error.FAILED)

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
        times       = data["times"]
        opttype     = data["opttype"]
        from_token_id = data["token_id"]
        map_token_id = stmanage.get_token_map(from_token_id) #stable token -> LBRXXX token

        ret = result(error.FAILED)
        self._logger.info(f"start exchange {self.dtype}. version={version}, state = {state}, detail = {detail} datas from server.")

        if state is not None:
            self.latest_version[receiver] = max(version, self.latest_version.get(receiver, -1))

        #if found transaction in history.db, then get_transactions's latest_version is error(too small or other case)'
        if state is None and self.has_info(tran_id):
            return ret

        if not self.chain_data_is_valid(data):
           return 

        self._logger.debug(f"exec_exchange-start...")
        if self.use_module(state, localdb.state.START):
            self.insert_to_localdb_with_check(version, localdb.state.START, tran_id, receiver)

        if self.use_module(state, localdb.state.PSUCCEED) or \
                self.use_module(state, localdb.state.ESUCCEED) or \
                self.use_module(state, localdb.state.FILLSUCCEED):

            #mint LBRXXX to sender(type = LBRXXX), or check sender's token amount is enough
            self._logger.debug(f"exec_exchange-1. start fill_address_token {map_token_id} to {map_sender.address.hex()} amount = {amount}...")
            ret = self.fill_address_token[self.map_chain](map_sender.address.hex(), map_token_id, amount)
            if ret.state != error.SUCCEED:
                self.update_localdb_state_with_check(tran_id, localdb.state.FILLFAILED, \
                      json.dumps(detail))
                self._logger.error("exec_exchange-1.result: failed.")
                return ret
            else:
                self.update_localdb_state_with_check(tran_id, localdb.state.FILLSUCCEED, \
                      json.dumps(detail))

            #send violas map token to payee address. P = payee
            markdata = self.map_client.create_data_for_mark(self.map_chain, self.dtype, \
                    tran_id, version)

            self._logger.debug(f"exec_exchange-2. start send {map_token_id} to {toaddress} amount = {amount}...")
            ret = self.map_client.send_coin(map_sender, toaddress, \
                    amount, map_token_id, data=markdata)

            if ret.state != error.SUCCEED:
                self._logger.error("exec_exchange-2.result: failed.")
                self.update_localdb_state_with_check(tran_id, localdb.state.PFAILED, \
                        json.dumps(detail))
                return ret
            else:
                self.update_localdb_state_with_check(tran_id, localdb.state.PSUCCEED)
        #send libra token to toaddress
        #sendexproofmark succeed , send violas coin with data for change tran state
        if self.use_module(state, localdb.state.VSUCCEED):
            self._logger.debug(f"exec_exchange-3. start send_coin_for_update_state_to_end...")
            ret =  self.send_coin_for_update_state_to_end(from_sender, receiver, tran_id, \
                    from_token_id, 1, out_amount_real=amount)
            if ret.state != error.SUCCEED:
                return ret

        self._logger.debug(f"exec_exchange-end...")
        return result(error.SUCCEED)

