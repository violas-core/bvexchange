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
from exchange.vlbase import vlbase

#module self.name
#name="exlv"
wallet_name = "vwallet"

VIOLAS_ADDRESS_LEN = comm.values.VIOLAS_ADDRESS_LEN
#load logging
class v2l(vlbase):    
    def __init__(self, name, dtype, vlsnodes, lbrnodes, proofdb, receivers, senders, combine):
        vlbase.__init__(self, name, dtype, vlsnodes, lbrnodes, proofdb, receivers, senders, "violas", "libra")
        self.append_property("combine ", combine)

        ret  = self.from_wallet.get_account(self.combine)
        self.check_state_raise(ret, f"get combin({self.combine})'s account failed.")
        self.append_property("combine_account", ret.datas)

    def __del__(self):
        pass

    def __get_reexchange(self):
        try:
            maxtimes = 5
            rpcparams = {}
            #transactions that should be __get_reexchange(xxx.db)
            
            ## failed 
            if stmanage.get_max_times(self.name()) > 0:
                maxtimes = stmanage.get_max_times(self._name)

            states = []
            states.append(localdb.state.FAILED)
            states.append(localdb.state.QBFAILED)
            states.append(localdb.state.FILLFAILED)
            states.append(localdb.state.PFAILED)
            states.append(localdb.state.VFAILED)
            states.append(localdb.state.SFAILED)
            for state in states:
                self.load_record_and_merge(rpcparams, state, maxtimes)

            ret = result(error.SUCCEED, "", rpcparams)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def fill_address_token_violas(self, address, token_id, amount, gas=40_000):
        try:
            ret = self.violas_client.get_balance(address, token_id = token_id)
            assert ret.state == SUCCEED, f"get balance failed"
            
            cur_amount = ret.datas
            if cur_amount < amount + gas:
                ret = self.from_client.mint_coin(address, amount = amount + gas - cur_amount, token_id = token_id)
                return ret

            return result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def exec_exchange(self, data, from_sender, map_sender, combine_account, receiver, state = None, detail = {}):
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
        from_token_id = stmanage.get_token_map(stable_token_id) #stable token -> LBRXXX token
        to_token_id    = self.to_token_id #token_id is map 

        ret = result(error.FAILED)
        self._logger.info(f"start exchange sender={fromaddress},  receiver={receiver}, sequence={sequence} " + \
                f"version={version}, toaddress={toaddress}, amount={amount}, tran_id={tran_id}, " + \
                f"from_token_id = {from_token_id} to_token_id={to_token_id} datas from server.")

        self._latest_version[receiver] = max(version, self._latest_version.get(receiver, -1))

        #if found transaction in history.db, then get_transactions's latest_version is error(too small or other case)'
        if state is None and self.has_info(tran_id):
            return ret

        if not self.chain_data_is_valid(data):
            return ret 

        #get swap before amount(to_token_id)
        
        if self.use_module(state, localdb.state.FAILED):
            ret = self.map_client.get_balance(combine_account.address.hex(), to_token_id)
            if ret.state != error.SUCCEED:
                self.insert_to_localdb_with_check(version, localdb.state.FAILED, tran_id, receiver)
                return ret
            before_amount = ret.balance
            detail.update({"before_amount": before_amount})

            #get gas for swap
            ret = self.map_client.swap_get_output_amount(from_token_id, to_token_id, amount)
            if ret.state != error.SUCCEED:
                self.insert_to_localdb_with_check(version, localdb.state.FAILED, tran_id, receiver)
            _, gas = ret.datas
            detail.update({"gas", gas})

            #swap LBRXXX -> VLSYYY
            ret = self.from_client.swap(map_sender, from_token_id, to_token_id, amount, out_amount, receiver = combine_account.address.hex(), gas_currency_code = from_token_id)
            if ret.state != error.SUCCEED:
                self.insert_to_localdb_with_check(version, localdb.state.FAILED, tran_id, receiver)
                return ret
            else:
                self.insert_to_localdb_with_check(version, localdb.state.SUCCEED, tran_id, receiver)

            #get swap after amount(to_token_id)
            ret = self.map_client.get_balance(combine_account.address.hex(), to_token_id)
            if ret.state != error.SUCCEED:
                ret = self.from_client.get_address_version(combine_account.address.hex())
                self.check_state_raise(ret, f"get_address_version({combine_account.address.hex})")
                detail.update({"swap_version": ret.datas})

                #if get balance, next execute, balance will change , so re swap, but combine token(to_token_id) is change, this time swap token_id should be burn
                self.update_localdb_state_with_check(tran_id, localdb.state.QBFAILED, json.dumps(detail)) #should get swap to_token balance from version
                return ret
            after_amount = ret.balance

            #clac diff balance
            diff_balance = after_amount - before_amount
            detail.update({"diff_balance": diff_balance})
        
        if self.use_module(state, localdb.state.QBFAILED):
            diff_balance = 1
            assert state != localdb.state.QBFAILED, "get swap token count from detail['swap_version'], here we think get_balance is always succeed"

        #mint LBRXXX to sender(type = LBRXXX), or check sender's token amount is enough
        if self.use_module(state, localdb.state.FILLFAILED):
            ret = self.fill_address_token(map_sender.address.hex(), to_token_id, detail["diff_balance"], detail["gas"])
            if ret.state != error.SUCCEED:
                self.update_localdb_state_with_check(tran_id, localdb.state.FILLFAILED, json.dumps(detail))
                return ret

        #send libra token to payee address. P = payee
        if self.use_module(state, localdb.state.PFAILED):
            markdata = self.map_client.create_data_for_mark(self.map_chain, self.dtype, tran_id, version)
            ret = self.map_client.send_coin(combine_account, toaddress, detail["diff_balance"], to_token_id, data=markdata)
            if ret.state != error.SUCCEED:
                self.update_localdb_state_with_check(tran_id, localdb.state.PFAILED, json.dumps(detail))
                return ret
            else:
                self.update_localdb_state_with_check(tran_id, localdb.state.PSUCCEED)

        #send libra token to toaddress
        #sendexproofmark succeed , send violas coin with data for change tran state
        if self.use_module(state, localdb.state.VFAILED):
            self.send_coin_for_update_state_to_end(from_sender, receiver, tran_id, from_token_id)

def main():
       print("start main")
       lv = exlv()
       
       ret = lv.start()
       if ret.state != error.SUCCEED:
           print(ret.message)

if __name__ == "__main__":
    main()
