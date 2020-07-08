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
from db.dbv2l import dbl2v as localdb
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
    def __init__(self, name, dtype, vlsnodes, lbrnodes, proofdb, receivers, senders):
        vlbase.__init__(self, name, dtype, vlsnodes, lbrnodes, proofdb, receivers, senders, "libra", "violas")

    def __del__(self):
        pass

    def __fill_address_token(self, address, token_id, amount, gas=40_000):
        try:
            ret = self.from_client.get_balance(address, token_id = token_id)
            assert ret.state == SUCCEED, f"get balance failed"
            
            cur_amount = ret.datas
            if cur_amount < amount + gas:
                ret = self.from_client.mint_coin(address, amount = amount + gas - cur_amount, token_id = token_id)
                return ret

            return result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def reexchange_data_from_failed(self, gas = 1000):
        try:
            #get all excluded info from db
            rpcparams = {}
            ret = self.__get_reexchange()
            if(ret.state != error.SUCCEED):
                return ret
            rpcparams = ret.datas
            receivers = self.receivers

            #modulti receiver, one-by-one
            ret = self._pserver.get_latest_saved_ver()
            if(ret.state != error.SUCCEED):
                self._logger.debug(f"get_latest_saved_ver from request client failed.")
                return ret
            latest_version = ret.datas
            self._logger.debug(f"get latest saved version from db is : {latest_version}")
            
            #get map sender from  senders
            ret = self.__get_map_sender_address()
            self.check_state_raise(ret, f"not found map sender{toaddress} or amount too low. check address and amount")
            map_sender = ret.datas
            self._logger.debug(f"map_sender({type(map_sender)}): {map_sender.address.hex()}")

            for receiver in receivers:
                if not self.work() :
                    break
    
                ret  = self.from_wallet.get_account(receiver)
                if ret.state != error.SUCCEED:
                    self._logger.warning(f"get receiver({receiver})'s account failed.")
                    continue 
                fromsender = ret.datas

                #get old transaction from db, check transaction. version and receiver is current value
                faileds = rpcparams.get(receiver)
                if faileds is not None:
                    self._logger.debug("start exchange failed datas from db. receiver={}".format(receiver))
                    for failed in faileds:
                        if (self.work() == False):
                            break

                        times       = failed["times"]
                        ret = self.pserver.get_tran_by_tranid(tran_id)
                        if ret.state != error.SUCCEED:
                            continue
                        data = ret.datas

                        fromaddress = data["address"]
                        amount      = int(data["amount"]) 
                        version     = data["version"]
                        toaddress   = data["to_address"] #map token to
                        tran_id     = data["tran_id"]
                        out_amount  = data["out_amount"]
                        retry       = data["times"]
                        opttype     = data["opttype"]
                        stable_token_id = data["token_id"]
                        from_token_id = stmanage.get_token_map(stable_token_id) #stable token -> LBRXXX token
                        to_token_id    = self.to_token_id #token_id is map 

                        if retry > 0 and retry >= times:
                            continue

                        self._logger.info(f"start exchange exglv, datas from db. toaddress={toaddress}" + \
                                f"version={version}, receiver={receiver}, amount={vamount}, out_amount={out_amount}, opttype = {opttype}" + \
                                f"tran_id={tran_id} datas from server.")

                        if self.db_data_is_valid(data) == False:
                            self._logger.warning(f"transaction(tran_id = {tran_id})) is invalid. ignore it and process next.")
                            continue

                        #check version, get transaction list is ordered ?
                        if version > latest_version:
                            self._logger.warning(f"transaction's version({version}) must be Less than or equal to latest_version({latest_version}).")
                            continue
    

                        ret = self.map_client.swap_get_output_amount(from_token_id, to_token_id, amount)
                        assert ret.state == error.SUCCEED, f"swap_get_output_amount failed."
                        _, gas = ret.datas

                        #mint LBRXXX to sender(type = LBRXXX), or check sender's token amount is enough
                        ret = self.__fill_address_token(map_sender.address.hex(), from_token_id, amount, gas)
                        if ret.state != error.SUCCEED:
                            ret = self._db.insert_commit(version, dbv2l.state.FAILED, tran_id, receiver)
                            assert (ret.state == error.SUCCEED), "db error"
                            continue

                        #swap LBRXXX -> VLSYYY
                        ret = self.from_client.swap(map_sender, from_token_id, to_token_id, amount, out_amount, receiver = toaddress, gas_currency_code = from_token_id)

                        if ret.state != error.SUCCEED:
                            ret = self._db.update_state_commit(tran_id, localdb.state.SUCCEED)
                            assert (ret.state == error.SUCCEED), "db error"
                            continue
                        else:
                            ret = self._db.update_state_commit(tran_id, localdb.state.FAILED)
                            assert (ret.state == error.SUCCEED), "db error"
           
                        #sendexproofmark succeed , send violas coin with data for change violas state
                        self._send_coin_for_update_state_to_end(fromsender, receiver, tran_id, from_token_id)

            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret 

    def chain_data_is_valid(self, data):
        self._logger.debug(f"check address{data['to_address']}. len({data['to_address']}) in {VIOLAS_ADDRESS_LEN}?")
        if len(data["to_address"]) not in VIOLAS_ADDRESS_LEN:
            self._logger.warning(f"transaction(tran_id = {data["tran_id"]})) is invalid. ignore it and process next.")
            return False
        return True

    def has_info(tranid):
        ret = self._db.has_info(tranid)
        assert ret.state == error.SUCCEED, f"has_info({tranid}) failed."
        if ret.datas == True:
            self._logger.warning(f"found transaction(tran_id = {tran_id})) in db(maybe first run {self.dtype}). ignore it and process next.")
        return ret.datas

    def use_module(self, state, module_state):
        return state is None or state.value <= module_state.value

    def exec_exchange(data, from_sender, map_sender, receiver, state = None, detail = {}):
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

        self._logger.info(f"start exchange l2v.sender={fromaddress},  receiver={receiver}, sequence={sequence} " + \
                f"version={version}, toaddress={toaddress}, amount={amount}, tran_id={tran_id}, " + \
                f"from_token_id = {from_token_id} to_token_id={to_token_id} datas from server.")

        self._latest_version[receiver] = max(version, self._latest_version.get(receiver, -1))

        #if found transaction in history.db, then get_transactions's latest_version is error(too small or other case)'
        if self.has_info(tran_id):
            continue
    
        if not self.chain_data_is_valid(data):
            continue

        ret = self.map_client.swap_get_output_amount(from_token_id, to_token_id, amount)
        assert ret.state == error.SUCCEED, f"swap_get_output_amount failed."
        _, gas = ret.datas

        #mint LBRXXX to sender(type = LBRXXX), or check sender's token amount is enough
        ret = self.__fill_address_token(map_sender.address.hex(), from_token_id, amount, gas)
        if ret.state != error.SUCCEED:
            ret = self._db.insert_commit(version, dbv2l.state.FAILED, tran_id, receiver)
            assert (ret.state == error.SUCCEED), "db error"
            continue

        #swap LBRXXX -> VLSYYY and send VLSXXX to toaddress(client payee address)
        ret = self.from_client.swap(map_sender, from_token_id, to_token_id, amount, out_amount, receiver = toaddress, gas_currency_code = from_token_id)
        if ret.state != error.SUCCEED:
            ret = self._db.insert_commit(version, dbv2l.state.FAILED, tran_id, receiver)
            assert (ret.state == error.SUCCEED), "db error"
            continue
        else:
            ret = self._db.insert_commit(version, dbv2l.state.SUCCEED, tran_id, receiver)
            assert (ret.state == error.SUCCEED), "db error"
        
        #send libra token to toaddress
        #sendexproofmark succeed , send violas coin with data for change tran state
        self._send_coin_for_update_state_to_end(fromsender, receiver, tran_id, from_token_id)

    def start(self):
    
        try:
            self._logger.debug("start works")
            gas = 1000

            #requirement checks
            self.__checks()
    
            #db state: VFAILED
            #send token is succeed, but change transaction state is failed, 
            ##so resend transaction to change state = end
            self._rechange_tran_state()

            #db state: FAILED
            #if history datas is found state = failed, exchange it until succeed
            self.reexchange_data_from_failed(gas)
    
            #db state: SUCCEED
            #check state from blockchain, and change exchange history data, 
            ##when change it to complete, can truncature history db
            self._rechange_db_state()

            #get map sender from senders
            ret = self.__get_map_sender_address()
            self.check_state_raise(ret, f"not found map sender{toaddress} or amount too low. check address and amount")
            map_sender = ret.datas
            self._logger.debug(f"map_sender({type(map_sender)}): {map_sender.address.hex()}")

            receivers = self.receivers
            #modulti receiver, one-by-one
            for receiver in receivers:
                if not self.work() :
                    break

                ret  = self.from_wallet.get_account(receiver)
                self.check_state_raise(ret, f"get receiver({receiver})'s account failed.")
                fromsender = ret.datas
                latest_version = self._latest_version.get(receiver, -1) + 1

                #get new transaction from server
                ret = self._pserver.get_transactions_for_start(receiver, self.dtype, latest_version)
                if ret.state == error.SUCCEED and len(ret.datas) > 0:
                    self._logger.debug("start exchange datas from violas server. receiver={}".format(receiver))
                    for data in ret.datas:
                        if not self.work() :
                            break

                        #grant token 
                        ##check 
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

                        self._logger.info(f"start exchange l2v.sender={fromaddress},  receiver={receiver}, sequence={sequence} " + \
                                f"version={version}, toaddress={toaddress}, amount={amount}, tran_id={tran_id}, " + \
                                f"from_token_id = {from_token_id} to_token_id={to_token_id} datas from server.")

                        self._latest_version[receiver] = max(version, self._latest_version.get(receiver, -1))

                        #if found transaction in history.db, then get_transactions's latest_version is error(too small or other case)'
                        if self.has_info(tran_id):
                            continue
    
                        if not self.chain_data_is_valid(data):
                            continue

                        ret = self.map_client.swap_get_output_amount(from_token_id, to_token_id, amount)
                        assert ret.state == error.SUCCEED, f"swap_get_output_amount failed."
                        _, gas = ret.datas

                        #mint LBRXXX to sender(type = LBRXXX), or check sender's token amount is enough
                        ret = self.__fill_address_token(map_sender.address.hex(), from_token_id, amount, gas)
                        if ret.state != error.SUCCEED:
                            ret = self._db.insert_commit(version, dbv2l.state.FAILED, tran_id, receiver)
                            assert (ret.state == error.SUCCEED), "db error"
                            continue

                        #swap LBRXXX -> VLSYYY and send VLSXXX to toaddress(client payee address)
                        ret = self.from_client.swap(map_sender, from_token_id, to_token_id, amount, out_amount, receiver = toaddress, gas_currency_code = from_token_id)
                        if ret.state != error.SUCCEED:
                            ret = self._db.insert_commit(version, dbv2l.state.FAILED, tran_id, receiver)
                            assert (ret.state == error.SUCCEED), "db error"
                            continue
                        else:
                            ret = self._db.insert_commit(version, dbv2l.state.SUCCEED, tran_id, receiver)
                            assert (ret.state == error.SUCCEED), "db error"
           
                        #send libra token to toaddress
                        #sendexproofmark succeed , send violas coin with data for change tran state
                        self._send_coin_for_update_state_to_end(fromsender, receiver, tran_id, from_token_id)
    
            ret = result(error.SUCCEED) 
    
        except Exception as e:
            ret = parse_except(e)
        finally:
            self._logger.debug("works end.")
    
        return ret
    
def main():
       print("start main")
       lv = exlv()
       
       ret = lv.start()
       if ret.state != error.SUCCEED:
           print(ret.message)

if __name__ == "__main__":
    main()
