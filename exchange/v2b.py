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
import vlsopt.violasclient
from vlsopt.violasclient import violasclient, violaswallet, violasserver
from vlsopt.violasproof import violasproof
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from baseobject import baseobject
from enum import Enum
from vrequest.request_client import requestclient
from exchange.exbase import exbase

#module self.name
#name="exlv"
wallet_name = "vwallet"

VIOLAS_ADDRESS_LEN = comm.values.VIOLAS_ADDRESS_LEN
#load logging
class v2b(exbase):    
    def __init__(self, 
            name, 
            dtype, 
            vlsnodes, 
            btcnodes, 
            proofdb, 
            receivers, 
            senders, 
            combine, 
            swap_module,
            swap_owner):
        ''' violas stable token swap to bitcoin BTC
            @dtype : opttype
            @vlsnodes: violas nodes configure
            @btcnodes: btc node configure
            @proofdb: violas proof configure
            @receivers: violas receivers address
            @senders: btc address, use this address to transfer
            @combine: violas address, use this address store swap token 
            @swap_module: swap module address
            @swap_owner: swap owner address
        '''
        exbase.__init__(self, name, dtype, \
                btcnodes, vlsnodes, None, \
                proofdb, receivers, senders, \
                swap_module, swap_owner,\
                "violas", "btc")
        self.append_property("combine", combine)

        self.init_extend_property()
        self.init_exec_states()

    def __del__(self):
        pass

    def init_extend_property(self):
        ret = self.violas_wallet.get_account(self.combine)
        self.check_state_raise(ret, f"get combine({self.combine})'s account failed.")
        self.append_property("combine_account", ret.datas)

    def init_exec_states(self):

        self.append_property("use_exec_update_db_states", 
                [localdb.state.VSUCCEED, localdb.state.SSUCCEED])

        self.append_property("use_exec_failed_state", 
            [state for state in localdb.state \
                    if state not in [localdb.state.COMPLETE, \
                        localdb.state.VSUCCEED, \
                        localdb.state.SSUCCEED, \
                        localdb.state.PSUCCEED]])

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
        sender      = data["address"]
        amount      = int(data["amount"]) 
        sequence    = data["sequence"] 
        version     = data["version"]
        toaddress   = data["to_address"] #map token to
        tran_id     = data["tran_id"]
        out_amount  = data["out_amount"]
        times       = data["times"]
        opttype     = data["opttype"]
        from_token_id = data["token_id"] #VLSXXX
        to_token_id = self.to_token_id
        map_token_id = stmanage.get_token_map(to_token_id) #stable token -> map token
        assert map_token_id is not None, f"get token({to_token_id}) failed, check config token_map"

        ret = result(error.FAILED)
        self._logger.info(f"start exchange {self.dtype}, version={version}, state(None: new swap) = {state}, detail = {detail} datas from server.")

        #only violas and libra use this , btc can't use version
        if state is not None:
            self.latest_version[receiver] = max(version, self.latest_version.get(receiver, -1))

        #if found transaction in history.db(state == None), 
        #then get_transactions's latest_version is error(too small or other case)' 
        if state is None and self.has_info(tran_id):
            return ret

        if not self.chain_data_is_valid(data):
            return ret 

        if self.use_module(state, localdb.state.START):
            self.insert_to_localdb_with_check(version, localdb.state.START, tran_id, receiver)

        if self.use_module(state, localdb.state.QBSUCCEED):
            if not detail.get("swap_version"):
                #get gas for swap
                self._logger.debug(f"exec_exchange-1. start swap_get_output_amount({from_token_id} {to_token_id} {amount})...")
                ret = self.violas_client.swap_get_output_amount(from_token_id, map_token_id, amount)
                if ret.state != error.SUCCEED:
                    self.update_localdb_state_with_check(tran_id, localdb.state.FAILED)
                    return ret 

                out_amount_chian, gas = ret.datas

                #temp value(test)
                #btc -> vbtc(1000000), violas swap vbtc
                out_amount = self.amountswap(out_amount, self.amountswap.amounttype[self.map_chain.upper()]).violas_amount

                self._logger.debug(f"exec_exchange-0.result : can swap amount: = {out_amount_chian} gas = {gas}, want = {out_amount}vBTC")

                if out_amount <= 0:
                    out_amount = out_amount_chian
                elif out_amount > out_amount_chian or out_amount_chian < 0: #don't execute swap, Reduce the cost of the budget
                    detail.update({"error" : f"out_amount({out_amount}) > out_amount_chain({out_amount_chian})"})
                    self.update_localdb_state_with_check(tran_id, localdb.state.FAILED, \
                            json.dumps(detail))
                    return result(error.FAILED, \
                            f"don't execute swap(out_amount({out_amount}) > cur_outamount({out_amount_chian})), " 
                            + f"Reduce the cost of the budget. tran_id = {tran_id}")

                detail.update({"gas": gas})

                self._logger.debug(f"exec_exchange-1. start swap({from_token_id}, {map_token_id}, {amount}...")
                ret = self.violas_client.swap(from_sender, from_token_id, map_token_id, amount, \
                        out_amount, receiver = combine_account.address.hex(), \
                        gas_currency_code = from_token_id)

                if ret.state != error.SUCCEED:
                    self.update_localdb_state_with_check(tran_id, localdb.state.FAILED, \
                            json.dumps(detail))
                    self._logger.error("exec_exchange-1.result: failed.")
                    return ret

                self._logger.debug(f"exec_exchange-2. start get transaction version({from_sender.address.hex()})...")
                ret = self.violas_client.get_address_version(from_sender.address.hex())
                if ret.state != error.SUCCEED:
                    self._logger.error("exec_exchange-2.result: failed.")
                    self.update_localdb_state_with_check(tran_id, localdb.state.FAILED)
                    return ret
                swap_version = ret.datas 

                detail.update({"swap_version": swap_version})

            #get swap after amount(map_token_id)
            self._logger.debug("exec_exchange-x. get swap balance..")
            ret = self.get_swap_balance(detail["swap_version"])
            if ret.state != error.SUCCEED:
                #if get balance, next execute, balance will change , so re swap, 
                #but combine token(map_token_id) is change, this time swap token_id should be burn
                self.update_localdb_state_with_check(tran_id, localdb.state.QBFAILED, \
                        json.dumps(detail)) #should get swap to_token balance from version
                return ret
            else:
                detail.update({"diff_balance": ret.datas})
                self.update_localdb_state_with_check(tran_id, localdb.state.QBSUCCEED, \
                        json.dumps(detail))

        #mint LBRXXX to sender(type = LBRXXX), or check sender's token amount is enough, re fill ????
        if self.use_module(state, localdb.state.FILLSUCCEED) or \
                self.use_module(state, localdb.state.PSUCCEED):

            self._logger.debug(f"exec_exchange-3. start fill_address_token...")
            send_amount = self.amountswap(detail["diff_balance"]).amount(self.map_chain)
            ret = self.fill_address_token[self.map_chain](map_sender, to_token_id, send_amount)
            if ret.state != error.SUCCEED:
                self.update_localdb_state_with_check(tran_id, localdb.state.FILLFAILED, \
                        json.dumps(detail))
                self._logger.error(f"exec_exchange-3. result: failed. {ret.message}")
                return ret
            else:
                self.update_localdb_state_with_check(tran_id, localdb.state.FILLSUCCEED, \
                        json.dumps(detail))


        #send btc token to payee address. P = payee
            markdata = self.btc_client.create_data_for_mark(self.violas_chain, self.dtype, \
                    sender, version)

            self._logger.debug(f"exec_exchange-4. start send btc to {toaddress} amount = {send_amount:.8f}...")
            ret = self.btc_client.send_coin(map_sender, toaddress, \
                    send_amount, to_token_id, data=markdata)
            if ret.state != error.SUCCEED:
                self.update_localdb_state_with_check(tran_id, localdb.state.PFAILED, \
                        json.dumps(detail))
                self._logger.error("exec_exchange-4.result: failed.")
                return ret
            else:
                self.update_localdb_state_with_check(tran_id, localdb.state.PSUCCEED, \
                        json.dumps(detail))

        #send libra token to toaddress
        #sendexproofmark succeed , send violas coin with data for change tran state
        if self.use_module(state, localdb.state.VSUCCEED):
            self._logger.debug(f"exec_exchange-5. start send_coin_for_update_state_to_end({receiver}, {tran_id})...")
            ret = self.send_coin_for_update_state_to_end(from_sender, receiver, tran_id, \
                    from_token_id, version = version, out_amount_real=self.amountswap(detail["diff_balance"]).microamount(self.map_chain))
            if ret.state != error.SUCCEED:
                return ret
        self._logger.debug("exec_exchange-end.")
        return result(error.SUCCEED)

def main():
       print("start main")
       
       stmanage.set_conf_env("../bvexchange.toml")
       mod = "v2b"
       dtype = "v2b"
       obj = v2b(mod, 
               dtype,
               stmanage.get_violas_nodes(), 
               stmanage.get_btc_nodes(),
               stmanage.get_db(dtype), 
               list(set(stmanage.get_receiver_address_list(dtype, "violas", False))),
               list(set(stmanage.get_sender_address_list(dtype, "btc", False))),
               stmanage.get_combine_address(dtype, "violas"),
               stmanage.get_swap_module(),
               stmanage.get_swap_owner()
               )
       ret = obj.start()
       if ret.state != error.SUCCEED:
           print(ret.message)

if __name__ == "__main__":
    main()
