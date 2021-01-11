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
from funds.exfbase import exfbase

class exfunds(exfbase):    
    def __init__(self, name, 
            dtype, 
            proofdb, 
            receivers, 
            fromchain,
            tochain,
            **kwargs
            ):

        ''' swap token and send coin to payee(metadata's to_address)
            proofdb  : transaction proof source(proof db conf)
            receivers: addresses of receive funds request 
            fromchain: source chain name: violas
            tochain: target chain name: violas btc ethereum ethereum
            kwargs:
                btc_nodes: connect btc node info
                violas_nodes: connect violas node info
                libra_nodes: connect libra node info
                ethereum_nodes: connect ethereum node info
                btc_senders: btc chain accounts
                violas_senders: violas chain accounts
                libra_senders: libra chain accounts
                ethereum_senders: ethereum chain accounts
                request_funds_sender: have request funds permission account address.
        '''

        exfbase.__init__(self, name, dtype, \
                proofdb, receivers, \
                fromchain, \
                tochain, \
                **kwargs)
        self.init_exec_states()

    def __del__(self):
        pass

    def init_exec_states(self):
        self.append_property("use_exec_update_db_states", 
                [localdb.state.VSUCCEED, localdb.state.SSUCCEED])

        self.append_property("use_exec_failed_state", 
            [state for state in localdb.state \
                    if state not in [localdb.state.COMPLETE, \
                        localdb.state.VSUCCEED, \
                        localdb.state.SSUCCEED]])

    def exec_exchange(self, data, from_sender, funds_sender, receiver, \
            state = None, detail = {}):
        fromaddress = data["address"]
        amount      = int(data["amount"]) 
        sequence    = data["sequence"] 
        version     = data["version"]
        toaddress   = data["to_address"] #map token to
        tran_id     = data["tran_id"]
        times       = data["times"]
        opttype     = data["opttype"]
        target_chain = data["chain"]
        token_id = data["token_id"]

        target_client = self.get_property(self.create_client_key(target_chain))
        assert target_client is not None, f"target chain{target_chain} is invalid."

        ret = result(error.FAILED)
        self._logger.info(f"start exfunds {self.dtype}. version={version}, state = {state}, detail = {detail} datas from server.")

        #if found transaction in history.db, then get_transactions's latest_version is error(too small or other case)'
        if state is None and self.has_info(tran_id):
            return ret

        if not self.chain_data_is_valid(data):
           return 

        amount_swap = self.amountswap(amount, self.amountswap.amounttype[target_chain.upper()], target_client.get_decimals(token_id))
        send_amount = amount_swap.amount(target_chain, target_client.get_decimals(token_id))
        micro_amount = amount_swap.microamount(target_chain, target_client.get_decimals(token_id))

        self._logger.debug(f"exec_exchange-start...")
        if self.use_module(state, localdb.state.START):
            self.insert_to_localdb_with_check(version, localdb.state.START, tran_id, receiver)

        if self.use_module(state, localdb.state.PSUCCEED) or \
                self.use_module(state, localdb.state.ESUCCEED) or \
                self.use_module(state, localdb.state.FILLSUCCEED):

            self._logger.debug(f"exec_exchange-1. start check_address_token_is_enough {target_chain} {funds_sender} {amount}...")
            ret = self.check_address_token_is_enough(target_client, funds_sender, token_id, amount)
            if ret.state != error.SUCCEED:
                self.update_localdb_state_with_check(tran_id, localdb.state.FILLFAILED, \
                      json.dumps(detail))
                self._logger.error(f"exec_exchange-1.result: failed. {ret.message}")
                return ret
            elif not ret.datas:
                detail.update({"msg": "token is not enough."})
                self._logger.error(f"exec_exchange-1.result: False。")
                self.update_localdb_state_with_check(tran_id, localdb.state.FILLSUCCEED, \
                      json.dumps(detail))
                return result(error.FAILED, "not enough token({token_id}) amount({amount}) chain({target_chain})")

            #send violas map token to payee address. P = payee
            markdata = target_client.create_data_for_mark(target_chain, self.dtype, \
                    tran_id, version)

            self._logger.debug(f"exec_exchange-2. start send {token_id} to {toaddress} amount = {send_amount}...")
            ret = target_client.send_coin(funds_sender, toaddress, \
                    send_amount, token_id, data=markdata)

            if ret.state != error.SUCCEED:
                self._logger.error(f"exec_exchange-2.result: failed.")
                self.update_localdb_state_with_check(tran_id, localdb.state.PFAILED, \
                        json.dumps(detail))
                return ret
            else:
                detail.update({"txid":ret.datas})
                self.update_localdb_state_with_check(tran_id, localdb.state.PSUCCEED, \
                        json.dumps(detail))

        #send libra token to toaddress
        #sendexproofmark succeed , send violas coin with data for change tran state
        if self.use_module(state, localdb.state.VSUCCEED):
            self._logger.debug(f"exec_exchange-3. start send_coin_for_update_state_to_end...")
            ret =  self.send_coin_for_update_state_to_end(from_sender, receiver, tran_id, \
                    token_id, 1, out_amount_real=micro_amount, version=version)
            if ret.state != error.SUCCEED:
                return ret

        self._logger.debug(f"exec_exchange-end...")
        return result(error.SUCCEED)

