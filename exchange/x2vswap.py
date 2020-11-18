#!/usr/bin/python3
import operator
import sys, os
import json
sys.path.append(os.getcwd())
sys.path.append("..")
import log
import log.logger
import datetime
import stmanage
from comm.result import result, parse_except
from comm.error import error
from db.dblocal import dblocal as localdb
from exchange.exbase import exbase

#module self.name
#name="l2v"
wallet_name = "vwallet"

#load logging
class x2vswap(exbase):    
    def __init__(self, name, 
            dtype, 
            btcnodes, 
            vlsnodes, 
            lbrnodes, 
            proofdb, 
            receivers, 
            senders, 
            swap_module,
            swap_owner,
            from_chain,
            map_chain):

        '''libra Coin1/Coin2 swap to violas stable token 
            @dtype : opttype
            @btcnodes: btc node configure
            @vlsnodes: violas node configure
            @lbrnodes: libra nodes configure
            @proofdb: violas proof configure, no-use
            @receivers: btc address, get valid swap transaction
            @senders: violas senders address, use this address to transfer(diff chain)
            @combine: btc address, change state transaction's payer
            @swap_module: swap module address
            @swap_owner: swap owner address
        '''
        exbase.__init__(self, name, dtype, \
                btcnodes, vlsnodes, lbrnodes, None,\
                proofdb, receivers, senders, \
                swap_module, swap_owner,\
                from_chain, map_chain)

    def exec_exchange(self, data, from_sender, map_sender, combine_account, receiver, \
            state = None, detail = {}):
        ''' execute exchange 
            @data : proof datas
            @from_sender: 
            @map_sender:
            @combine_account: inner  no-use
            @receiver: swap transaction's server address
            @state: check is new exchange or re-execute exchange with it, 
                    None is new, other is re-execute
            detail: when state is not None , get some info from detail
        '''
        fromaddress = data["address"]
        amount      = int(data["amount"]) 
        sequence    = data["sequence"] 
        version     = data["version"]
        toaddress   = data["to_address"] #map token to
        tran_id     = data["tran_id"]
        out_amount  = int(data.get("out_amount", 0))
        times       = data["times"]
        opttype     = data["opttype"]
        stable_token_id = data["token_id"]
        from_token_id = stable_token_id
        map_token_id = stmanage.get_token_map(stable_token_id, self.dtype) #stable token -> mapping token
        to_token_id    = self.to_token_id #token_id is map 

        amount = self.amountswap(amount, self.amountswap.amounttype[self.from_chain.upper()]).microamount(self.map_chain)
        self._logger.info(f"start exchange {self.dtype}, version={version}, state(None: new swap) = {state}, detail = {detail} datas from server.")

        if state is not None:
            self.latest_version[receiver] = max(version, self.latest_version.get(receiver, -1))

        #if found transaction in history.db, then get_transactions's latest_version is error(too small or other case)'
        if state is None and self.has_info(tran_id):
            return result(error.FAILED)

        if not self.chain_data_is_valid(data):
            return result(error.FAILED)

        if self.use_module(state, localdb.state.START):
            self.insert_to_localdb_with_check(version, localdb.state.START, tran_id, receiver)

        if self.use_module(state, localdb.state.PSUCCEED) or \
                self.use_module(state, localdb.state.ESUCCEED) or \
                self.use_module(state, localdb.state.FILLSUCCEED):
            #get output and gas
            self._logger.debug(f"exec_exchange-0. start swap_get_output_amount({map_token_id} {to_token_id} {amount})...")
            ret = self.violas_client.swap_get_output_amount(map_token_id, to_token_id, amount)
            if ret.state != error.SUCCEED:
                self.update_localdb_state_with_check(tran_id, localdb.state.FAILED)
                return ret
            else:
                self.update_localdb_state_with_check(tran_id, localdb.state.ESUCCEED)

            out_amount_chian, gas = ret.datas
            self._logger.debug(f"exec_exchange-0.result : can swap amount: = {out_amount_chian} gas = {gas}, want = {out_amount}{map_token_id}")

            #temp value(test)
            if out_amount <= 0:
                out_amount = out_amount_chian
            elif out_amount > out_amount_chian: #don't execute swap, Reduce the cost of the budget
                self.update_localdb_state_with_check(tran_id, localdb.state.FAILED, \
                        json.dumps(detail))
                return result(error.FAILED, \
                        f"don't execute swap(out_amount({out_amount}) > cur_outamount({out_amount_chian})), " 
                        + f"Reduce the cost of the budget. tran_id = {tran_id}")
            detail.update({"gas": gas})
            detail.update({"diff_balance": out_amount_chian})

            #mint LBRXXX to sender(type = LBRXXX), or check sender's token amount is enough
            self._logger.debug(f"exec_exchange-1. start fill_address_token...")
            ret = self.fill_address_token[self.map_chain](map_sender.address.hex(), map_token_id, amount, tran_id, detail["gas"])
            if ret.state != error.SUCCEED:
                self.update_localdb_state_with_check(tran_id, localdb.state.FILLFAILED, \
                      json.dumps(detail))
                self._logger.error(f"exec_exchange-1. result: failed. {ret.message}")
                return ret
            else:
                self.update_localdb_state_with_check(tran_id, localdb.state.FILLSUCCEED, \
                      json.dumps(detail))

            #swap LBRXXX -> VLSYYY and send VLSXXX to toaddress(client payee address)
            self._logger.debug(f"exec_exchange-2. start swap({map_token_id}, {to_token_id}, {amount}...")
            ret = self.violas_client.swap(map_sender, map_token_id, to_token_id, amount, \
                    out_amount, receiver = toaddress, gas_currency_code = map_token_id)
            if ret.state != error.SUCCEED:
                self.update_localdb_state_with_check(tran_id, localdb.state.PFAILED, \
                        json.dumps(detail))
                self._logger.error("exec_exchange-1.result: failed.")
                return ret
            else:
                #mark sure state changed 
                self.update_localdb_state_with_check(tran_id, localdb.state.PSUCCEED, \
                        json.dumps(detail))
                ret = self.violas_client.get_address_version(map_sender.address.hex())
                if ret.state == error.SUCCEED:
                    detail.update({"swap_version":ret.datas})
                    #update for swap_version
                    self.update_localdb_state_with_check(tran_id, localdb.state.PSUCCEED, \
                            json.dumps(detail))
                    ret = self.get_swap_balance(detail["swap_version"])
                    if ret.state == error.SUCCEED:
                        detail.update({"diff_balance": ret.datas})
                        #re-update diff_balance
                        self.update_localdb_state_with_check(tran_id, localdb.state.PSUCCEED, \
                                json.dumps(detail))

        #send libra token to toaddress
        #sendexproofmark succeed , send violas coin with data for change tran state
        if self.use_module(state, localdb.state.VSUCCEED):
            ret =  self.send_coin_for_update_state_to_end(from_sender, receiver, tran_id, from_token_id, 1, out_amount_real=detail.get("diff_balance", 0))
            if ret.state != error.SUCCEED:
                return ret

        return result(error.SUCCEED)

def main():
    print("start main")

if __name__ == "__main__":
    main()
