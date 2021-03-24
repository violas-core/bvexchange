#!/usr/bin/python3
import operator
import sys, os
import json
sys.path.append(os.getcwd())
sys.path.append("..")
import datetime
import stmanage
import comm
import comm.error
from comm.result import result, parse_except
from comm.error import error
from db.dblocal import dblocal as localdb
from exchange.exbase import exbase
from comm.values import (
        VIOLAS_ADDRESS_LEN
        )

from comm.values import (
        trantypebase as trantype,
        msgtype
        )

from dataproof import (
        dataproof
        )
class exmap(exbase):    
    def __init__(self, name, 
            dtype, 
            proofdb, 
            receivers, 
            senders, 
            fromchain,
            mapchain,
            **kwargs
            ):

        ''' map token and send coin to payee(metadata's to_address)
            proofdb  : transaction proof source(proof db conf)
            receivers: receive chain' addresses
            senders  : sender chain token adderss
            fromchain: source chain name
            mapchain : target chain name
            kwargs:
                btc_nodes: connect btc node info
                violas_nodes: connect violas node info
                libra_nodes: connect libra node info
                ethereum_nodes: connect ethereum node info
                funds_receiver: mint or recharge address
                combine: recover funds account
        '''
        exbase.__init__(self, name, dtype, \
                proofdb, receivers, senders, \
                fromchain, mapchain,\
                **kwargs)

        self.init_combine_account(kwargs.get("combine"))
        self.init_exec_states()

    def __del__(self):
        pass

    def init_combine_account(self, combine):
        if combine and self.is_valid_address(combine, trantype.VIOLAS):
            ret = self.violas_wallet.get_account(combine)
            self.check_state_raise(ret, f"get combine({combine})'s account failed.")
            self.append_property("combine_account", ret.datas)

    def init_exec_states(self):
        self.append_property("use_exec_update_db_states", 
                [localdb.state.VSUCCEED, localdb.state.SSUCCEED])

        self.append_property("use_exec_failed_state", 
            [state for state in localdb.state \
                    if state not in [localdb.state.COMPLETE, \
                        localdb.state.VSUCCEED, \
                        localdb.state.SSUCCEED]])

    #overwrited exbase.exec_exchange
    def exec_exchange(self, data, from_sender, map_sender, combine_account, receiver, \
            state = None, detail = {}):
        '''
        @dev execute mapping transaction
        @param data transaction data
        @param from_sender account of mapping receiver(DD account)
        @param map_sender account of target chain payer
        @param combine_account  account of combine, send token to the fund address provided by the association
        @param receiver address of from_sender
        @param state exchange state, None or other when state value. None : new transaction, not None: retry exchange(stored in local database)
        @param detail if state value is not None, detail value is error msg or preexchange value, maybe use it
        '''
        fromaddress = data["address"]
        amount      = int(data["amount"]) 
        sequence    = data["sequence"] 
        version     = data["version"]
        toaddress   = data["to_address"] #map token to
        tran_id     = data["tran_id"]
        times       = data["times"]
        opttype     = data["opttype"]
        from_token_id = data["token_id"]
        map_token_id = stmanage.get_token_map(from_token_id, self.dtype) 

        ret = result(error.FAILED)
        self._logger.info(f"start exchange {self.dtype}. version={version}, state = {state}, detail = {detail} datas from server.")

        #if found transaction in history.db, then get_transactions's latest_version is error(too small or other case)'
        if state is None and self.has_info(tran_id):
           return result(error.ARG_INVALID, f"found transaction(tran_id = {tran_id})) in local db(maybe first run {self.dtype}). ignore it and process next.")

        
        if not self.chain_data_is_valid(data):
            return result(error.ARG_INVALID, f"transaction({tran_id}) data is invalid. data :{data}")

        amount_swap = self.amountswap(amount, self.amountswap.amounttype[self.from_chain.upper()], self.from_client.get_decimals(from_token_id))
        map_amount = amount_swap.amount(self.map_chain, self.map_client.get_decimals(map_token_id))
        combine_amount = amount_swap.amount(self.from_chain, self.from_client.get_decimals(from_token_id))
        micro_amount = amount_swap.microamount(self.map_chain, self.map_client.get_decimals(map_token_id))

        self._logger.debug(f"exec_exchange-start...")
        if self.use_module(state, localdb.state.START):
            self.insert_to_localdb_with_check(version, localdb.state.START, tran_id, receiver)

        #transfer mint msg (datatype: x2vm)
        if self.is_need_mint_mtoken(self.dtype) and (state is None or self.use_module(state, localdb.state.MSUCCEED)):
            receiver_msg = self.get_address_from_account(self.funds_address)
            ret = self.send_violas_msg(map_sender, receiver_msg, msgtype.MINT, map_token_id, map_amount, tran_id, version)
            if ret.state != error.SUCCEED:
                detail.update({"mint_mtoken":localdb.state.MFAILED.name})
                self.update_localdb_state_with_check(tran_id, localdb.state.MFAILED, \
                      json.dumps(detail))
                self._logger.error(f"exec_exchange-0.result: failed. {ret.message}")
                return ret
            else:
                detail.update({"mint_mtoken":localdb.state.MSUCCEED.name})
                self.update_localdb_state_with_check(tran_id, localdb.state.MSUCCEED, \
                      json.dumps(detail))

        if self.use_module(state, localdb.state.PSUCCEED) or \
                self.use_module(state, localdb.state.ESUCCEED) or \
                self.use_module(state, localdb.state.FILLSUCCEED):

            #mint LBRXXX to sender(type = LBRXXX), or check sender's token amount is enough
            self._logger.debug(f"exec_exchange-1. start fill_address_token {map_token_id} to {self.get_address_from_account(map_sender)} amount = {map_amount}...")
            ret = self.fill_address_token[self.map_chain](map_sender, map_token_id, map_amount, tran_id, gas_token_id = dataproof.configs("gas_token_id").get(self.map_chain))
            if ret.state != error.SUCCEED:
                self.update_localdb_state_with_check(tran_id, localdb.state.FILLFAILED, \
                      json.dumps(detail))
                self._logger.error(f"exec_exchange-1.result: failed. {ret.message}")
                return ret
            else:
                self.update_localdb_state_with_check(tran_id, localdb.state.FILLSUCCEED, \
                      json.dumps(detail))

            #send violas map token to payee address. P = payee
            markdata = self.map_client.create_data_for_mark(self.map_chain, self.dtype, \
                    tran_id, version)

            self._logger.debug(f"exec_exchange-2. start send {map_token_id} to {toaddress} amount = {map_amount}...")
            ret = self.map_client.send_coin(map_sender, toaddress, \
                    map_amount, map_token_id, data=markdata)

            if ret.state != error.SUCCEED:
                self._logger.error(f"exec_exchange-2.result: failed.")
                self.update_localdb_state_with_check(tran_id, localdb.state.PFAILED, \
                        json.dumps(detail))
                return ret
            else:
                detail.update({"txid":ret.datas})
                self.update_localdb_state_with_check(tran_id, localdb.state.PSUCCEED, \
                        json.dumps(detail))

        #transfer burn msg(datatype : v2xm)
        if self.is_need_burn_mtoken(self.dtype) and (state is None or self.use_module(state, localdb.state.BSUCCEED)):
            receiver_msg = self.get_address_from_account(self.funds_address)
            ret = self.send_violas_msg(from_sender, receiver_msg, msgtype.BURN, from_token_id, amount, tran_id, version)
            if ret.state != error.SUCCEED:
                detail.update({"burn_mtoken":localdb.state.BFAILED.name})
                self.update_localdb_state_with_check(tran_id, localdb.state.BFAILED, \
                      json.dumps(detail))
                self._logger.error(f"exec_exchange-0.result: failed. {ret.message}")
                return ret
            else:
                detail.update({"burn_mtoken":localdb.state.BSUCCEED.name})
                self.update_localdb_state_with_check(tran_id, localdb.state.BSUCCEED, \
                      json.dumps(detail))

        #send libra token to toaddress
        #sendexproofmark succeed , send violas coin with data for change tran state
        if self.use_module(state, localdb.state.VSUCCEED):
            self._logger.debug(f"exec_exchange-3. start send_coin_for_update_state_to_end...")
            combine_address = self.get_combine_address(combine_account, receiver)
            ret =  self.send_coin_for_update_state_to_end(from_sender, combine_address, tran_id, \
                    from_token_id, combine_amount, out_amount_real=micro_amount, version=version)
            if ret.state != error.SUCCEED:
                return ret

        self._logger.debug(f"exec_exchange-end...")
        return result(error.SUCCEED)

