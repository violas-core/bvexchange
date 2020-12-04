#!/usr/bin/python3
import operator
import sys, os
import json
sys.path.append(os.getcwd())
sys.path.append("..")
import log
import log.logger
import stmanage
import requests
import comm
import comm.error
import comm.result
import comm.values
from time import sleep
from comm.result import result, parse_except
from comm.error import error
from comm.amountconver import amountconver 
from db.dblocal import dblocal as localdb
from db.dbfunds import dbfunds as localfunds
from wallet_factory import walletfactory
from client_factory import clientfactory
from vlsopt.violasclient import (
        violaswallet 
        )
from ethopt.ethclient import (
        ethclient, 
        ethwallet
        )
from btc.btcclient import btcclient
from btc.btcwallet import btcwallet
from vlsopt.violasproof import violasproof
from bitcoinrpc.authproxy import (
        AuthServiceProxy, 
        JSONRPCException
        )
from baseobject import baseobject
from enum import Enum
from vrequest.request_client import requestclient
from analysis.analysis_filter import afilter
from dataproof import dataproof
from comm.values import (
        datatypebase, 
        trantypebase as trantype
        )

#module self.name
#name="vbbase"

VIOLAS_ADDRESS_LEN = comm.values.VIOLAS_ADDRESS_LEN
#load logging
class exbase(baseobject):    

    class amountswap(amountconver):
        pass

    def __init__(self, name, dtype, \
            proofdb, receivers, senders, \
            fromchain, mapchain, \
            **kwargs):
        ''' swap token and send coin to payee(metadata's to_address)
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
                swap_module: violas chain swap module address
                swap_owner: violas chain swap owner address
                combine_account: swap:v2xxx mid account; map: combine funds to this account(violas)
            
        '''

        baseobject.__init__(self, name)
        self.latest_version = {}
        self.from_chain = fromchain.value if isinstance(fromchain, trantype) else fromchain
        self.map_chain = mapchain.value if isinstance(mapchain, trantype) else mapchain
    
        #violas/libra init
        self.append_property("receivers", receivers)
        self.append_property("senders ", senders)
        self.append_property("dtype", dtype)
        self.append_property("to_token_id ", stmanage.get_type_stable_token(dtype))
        self.append_property("proofdb", proofdb)

        #use the above property, so call set_local_workspace here
        self.set_local_workspace(**kwargs)

    def __del__(self):
        pass

    def stop(self):
        try:
            if self.violas_client:
                self.violas_client.stop()

            if self.btc_client:
                self.btc_client.stop()

            if self.libra_client:
                self.libra_client.stop()

            if self.ethereum_client:
                self.ethereum_client.stop()

            self.work_stop()
        except Exception as e:
            parse_except(e)

    def set_local_workspace(self, **kwargs):
        self.append_property("excluded", [])
        self.append_property("combine_account", kwargs.get("combine_account"))

        self.append_property(f"{self.from_chain}_chain", self.from_chain)
        self.append_property(f"{self.map_chain}_chain", self.map_chain)
        self.append_property("swap_module", kwargs.get("swap_module"))
        self.append_property("swap_owner", kwargs.get("swap_owner"))

        self.append_property("db", localdb(self.name(), f"{self.from_chain}_{self.dtype}.db"))
        self.append_property("funds_address", kwargs.get("funds"))
        self.append_property("db_funds", localfunds(self.name(), f"request_funds.db"))

        for ttype in trantype:
            if ttype == trantype.UNKOWN:
                continue

            #set property for senders 
            senders_name = self.create_senders_key(ttype.value)
            self.append_property(senders_name, kwargs.get(senders_name))

            #set property for wallet
            self.append_property(self.create_wallet_key(ttype.value), \
                    walletfactory.create(self.name(), ttype.value))

            #set property for client
            self.append_property(self.create_client_key(ttype.value), \
                    clientfactory.create(self.name(), ttype.value, kwargs.get(self.create_nodes_key(ttype.value))))

        if self.swap_module and self.violas_client:
            self.violas_client.swap_set_module_address(self.swap_module)
        if self.swap_owner and self.violas_client:
            self.violas_client.swap_set_owner_address(self.swap_owner)

        self.append_property("from_wallet", self.get_property(self.create_wallet_key(self.from_chain)))
        self.append_property("from_client", self.get_property(self.create_client_key(self.from_chain)))

        if trantype(self.from_chain) == trantype.BTC:
            self.append_property("pserver", self.btc_client)
        elif trantype(self.from_chain) in (trantype.VIOLAS, trantype.LIBRA, trantype.ETHEREUM):
            self.append_property("pserver", requestclient(self.name(), self.proofdb))
        else:
            raise Exception(f"chain {self.from_chain} is invalid.")

        if trantype(self.map_chain) != trantype.UNKOWN:
            self.append_property("map_wallet", self.get_property(self.create_wallet_key(self.map_chain)))
            self.append_property("map_client", self.get_property(self.create_client_key(self.map_chain)))

        self.init_fill_address_token()

    def load_vlsmproof(self, address):
        if self.ethereum_client:
            self.ethereum_client.load_vlsmproof(address)

    def append_contract(self, name):
        if self.ethereum_client:
            self.ethereum_client.load_contract(name)

    def init_fill_address_token(self):
        self.append_property("fill_address_token", {})
        self.fill_address_token.update({trantype.VIOLAS.value: self.fill_address_token_violas})
        self.fill_address_token.update({trantype.LIBRA.value: self.fill_address_token_libra})
        self.fill_address_token.update({trantype.BTC.value: self.fill_address_token_btc})
        self.fill_address_token.update({trantype.ETHEREUM.value: self.fill_address_token_ethereum})

    def insert_to_localdb_with_check(self, version, state, tran_id, receiver, detail = json.dumps({"default":"no-use"})):
        ret = self.db.insert_commit(version, state, tran_id, receiver, detail)
        assert (ret.state == error.SUCCEED), "db error"

    def update_localdb_state_with_check(self, tran_id, state, detail = json.dumps({"default":"no-use"})):
        ret = self.db.update_state_commit(tran_id, state, detail = detail)
        assert (ret.state == error.SUCCEED), "db error"

    #overwrite
    def get_map_sender_account(self):
        try:
            sender_account = None
            for sender in self.senders:
                return self.map_wallet.get_account(sender)

            return result(error.FAILED, "not found sender account")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def check_address_token_is_enough(self, client, address, token_id, amount):
        try:
            ret = client.get_balance(address, token_id = token_id)
            assert ret.state == SUCCEED, f"get balance failed"
            
            cur_amount = ret.datas
            return result(error.SUCCEED, datas = cur_amount >= amount)
        except Exception as e:
            ret = parse_except(e)
        return ret


    def merge_db_to_rpcparams(self, rpcparams, dbinfos):
        try:
            for info in dbinfos:
                new_data = {
                        "version":info.version, 
                        "tran_id":info.tranid, 
                        "state":info.state, 
                        "detail":info.detail,
                        "times":info.times}
                #server receiver address
                if info.receiver in rpcparams.keys():
                    rpcparams[info.receiver].append(new_data)
                else:
                    rpcparams[info.receiver] = [new_data]
    
            return result(error.SUCCEED, "", rpcparams)
        except Exception as e:
            ret = parse_except(e)
        return ret
    
    def load_record_and_merge(self, rpcparams, state, maxtimes = 999999999):
        try:
            ret = self.db.query_with_state(state, maxtimes)
            if(ret.state != error.SUCCEED):
                return ret 
    
            ret = self.merge_db_to_rpcparams(rpcparams, ret.datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def show_load_record_info(self, rpcparams):
        infos = {}
        for key, values in rpcparams.items():
            for value in values:
                info_key = f"{localdb.state(value.get('state')).name}"
                if info_key not in infos:
                    infos.update({info_key : 1})
                else:
                    infos[info_key] = infos[info_key] + 1
        self._logger.debug(f"record info:{infos}")


    def get_record_from_localdb_with_state(self, states):
        try:
            rpcparams = {}

            assert states is not None and len(states) > 0, f"args states is invalid."
            
            ## failed 
            maxtimes = stmanage.get_max_times()

            for state in states:
                ret = self.load_record_and_merge(rpcparams, state, maxtimes)
                if(ret.state != error.SUCCEED):
                    return ret
            
            ret = result(error.SUCCEED, datas = rpcparams)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def is_end(self, tran_id):
        return self.pserver.is_end(tran_id)

    def is_stop(self, tran_id):
        return self.pserver.is_stop(tran_id)

    def get_swap_balance(self, version):
        try:
            ret = self.violas_client.get_transaction(version)
            if ret.state != error.SUCCEED:
                return ret

            tran_data = afilter.get_tran_data(ret.datas)
            swap_data = tran_data.get("data")
            data = json.loads(swap_data)

            ret = result(error.SUCCEED, datas = data.get("out_amount"))
        except Exception as e:
            ret = parse_except(e)
        return ret

    # local db state is VSUCCEED , update state to COMPLETE
    def rechange_db_state(self, states):
        try:
            ##update violas blockchain state to end, if sendexproofmark is ok
            self._logger.debug(f"start rechange_db_state({[state.name for state in states]})")
            ret = self.get_record_from_localdb_with_state(states)
            if ret.state != error.SUCCEED:
                return ret
            rpcparams = ret.datas
            self.show_load_record_info(rpcparams)
            
            for key in rpcparams.keys():
                datas = rpcparams.get(key)
                for data in datas:
                    tran_id = data.get("tran_id")
                    if tran_id is None:
                        continue
                    ret = self.is_end(tran_id)
                    if ret.state == error.SUCCEED and ret.datas == True:
                       ret = self.update_localdb_state_with_check(tran_id, localdb.state.COMPLETE, detail = None)

                    ret = self.is_stop(tran_id)
                    if ret.state == error.SUCCEED and ret.datas == True:
                       ret = self.update_localdb_state_with_check(tran_id, localdb.state.COMPLETE, detail = None)

        except Exception as e:
            ret = parse_except(e)
        return ret

    def send_coin_for_update_state_to_end(self, sender, receiver, tran_id, token_id, amount = 1, **kwargs):
            self._logger.debug(f"start send_coin_for_update_state_to_end(sender={sender},"\
                    f"recever={receiver}, tran_id={tran_id}, amount={amount})")
            tran_data = self.from_client.create_data_for_end(self.from_chain, self.dtype, tran_id, **kwargs)
            ret = self.from_client.send_coin(sender, receiver, amount, token_id, data = tran_data)
            if ret.state != error.SUCCEED:
                self.update_localdb_state_with_check(tran_id, localdb.state.VFAILED, detail = None)
            else:
                self.update_localdb_state_with_check(tran_id, localdb.state.VSUCCEED, detail = None)
            return ret

    def __checks(self):
        return True
    
    def get_combine_address(self, combine_account, receiver):
        if combine_account:
            return self.get_address_from_account(combine_account)

        if receiver:
            return self.get_address_from_account(receiver)
        return None

    def get_address_from_account(self, account):
        if not isinstance(account, str):
            address = account.address
            if not isinstance(address, str):
                address = address.hex()
        else:
            address = account
        return address

    def __set_request_funds_account(self, from_sender, map_sender):
        if trantype(self.from_chain) == trantype.VIOLAS:
            self.append_property("request_funds_account", from_sender)
        elif trantype(self.map_chain) == trantype.VIOLAS:
            self.append_property("request_funds_account", map_sender)

    def __send_get_token(self, from_sender, chain, tran_id, token_id, amount, to_address):
        try:
            ret = self.db_funds.has_info(tran_id)
            if ret.state != error.SUCCEED:
                return ret

            if ret.datas:
                self._logger.debug(f"request funds for {tran_id} is existed. ")
                return result(error.SUCCEED)

            data = self.violas_client.create_data_for_funds(trantype.VIOLAS.value, datatypebase.FUNDS.value, chain, tran_id, token_id, amount, to_address)

            #send funds request must be use violas' token, maybe use VLS alwars???
            if chain != trantype.VIOLAS.value:
                usd_token = token_id
            else:
                usd_token = stmanage.get_token_map(token_id)

        
            ret = self.violas_client.send_coin(self.request_funds_account, self.funds_address, 1, stmanage.get_violas_mtoken(token_id, chain), data = data)
            if ret.state != error.SUCCEED:
                return ret

            ret = self.db_funds.insert_commit(tran_id, chain, token_id, amount, to_address)
            assert ret.state == error.SUCCEED, f"insert_commit({tranid}) failed"

        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_token_and_gas_amount(self, client, amount, token_id, gas_token_id):
        try:
            bdiff_token = gas_token_id is not None and gas_token_id != token_id

            address = self.get_address_from_account(account)
            ret = client.get_balance(address, token_id = token_id)
            assert ret.state == error.SUCCEED, f"get {address} balance({token_id}) failed"
            token_amount = ret.datas
            gas_amount = token_amount

            if bdiff_token:
                ret = client.get_balance(address, token_id = gas_token_id)
                assert ret.state == error.SUCCEED, f"get {address} gas balance({gas_token_id}) failed"
                gas_amount = ret.datas

            return result(error.SUCCEED, datas = (bdiff_token, token_amount, gas_amount))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def check_and_send_get_token(self, client, chain, account, token_id, amount, tran_id, gas, gas_token_id):
        try:
            ret = self.get_token_and_gas_amount(client, account, token_id, gas_token_id)
            if ret.state != error.SUCCEED:
                return ret
            bdiff_token, token_amount, gas_amount = ret.datas

            if bdiff_token and (gas_amount <= gas or token_amount < amount):
                msg = None
                if gas_amount < gas:
                    ret = self.__send_get_token(account, chain, f"{tran_id}_gas", gas_token_id, gas, address)
                    if ret.state != error.SUCCEED:
                        return ret
                    msg = f"address {address} not enough amount {gas_token_id}, olny have {gas_amount}{gas_token_id}."

                if token_amount < amount:
                    ret = self.__send_get_token(account, chain, tran_id, token_id, amount, address)
                    if ret.state != error.SUCCEED:
                        return ret
                    msg = f"address {address} not enough amount {token_id}, olny have {token_amount}{token_id}."
                return result(error.FAILED, msg)
            elif not bdiff_token and token_amount < amount + gas:
                ret = self.__send_get_token(account, chain, tran_id, token_id, amount + gas, address)
                if ret.state != error.SUCCEED:
                    return ret
                msg = f"address {address} not enough amount {token_id}, olny have {token_amount}{token_id}."
                return result(error.FAILED, msg)

            return result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def fill_address_token_violas(self, account, token_id, amount, tran_id, gas=100_0000, gas_token_id = None):
        return check_and_send_get_token(self.violas_client, trantype.VIOLAS.value, \
                account, token_id, amount, tran_id, gas, gas_token_id)

    def fill_address_token_libra(self, account, token_id, amount, tran_id, gas=100_000):
        return check_and_send_get_token(self.libra_client, trantype.LIBRA.value, \
                account, token_id, amount, tran_id, gas, gas_token_id)

    def fill_address_token_btc(self, account, token_id, amount, tran_id, gas=0.0001, gas_token_id = None):
        try:
            address = self.get_address_from_account(account)
            ret = self.btc_client.get_balance(address)
            assert ret.state == error.SUCCEED, f"get balance failed"
            
            cur_amount = ret.datas
            if cur_amount < amount + gas:
                micro_amount = self.amountswap(amount + gas, self.amountswap.BTC).microamount("btc", self.btc_client.get_decimals())
                ret = self.__send_get_token(account, trantype.BTC.value, tran_id, token_id, micro_amount, address)
                if ret.state != error.SUCCEED:
                    return ret
                return result(error.FAILED, f"address {address} not enough amount {token_id}, olny have {cur_amount}{token_id}.")

            return result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def fill_address_token_ethereum(self, account, token_id, amount, tran_id, gas=1_00_0000, gas_token_id = "eth"):
        return check_and_send_get_token(self.ethereum_client, trantype.ETHEREUM.value, \
                account, token_id, amount, tran_id, gas, gas_token_id)

    def db_data_is_valid(self, data):
        try:
            toaddress   = data["receiver"]
            self._logger.debug(f"check address{toaddress}. len({toaddress}) in {VIOLAS_ADDRESS_LEN}?")
        except Exception as e:
            pass
        return False

    def chain_data_is_valid(self, data):
        if False: # btc and violas is diff ????????
            self._logger.warning(f"transaction(tran_id = {data['tran_id']})) is invalid. " + 
                    f"ignore it and process next.")
            return False
        return True

    def has_info(self, tranid):
        ret = self.db.has_info(tranid)
        assert ret.state == error.SUCCEED, f"has_info({tranid}) failed."
        if ret.datas == True:
            self._logger.warning(f"found transaction(tran_id = {tranid})) in db(maybe first run {self.dtype}). " + 
                    f"ignore it and process next.")
        return ret.datas

    def use_module(self, state, module_state):
        return state is None or state.value < module_state.value

    def is_target_state(self, tranid, state):
        ret = self.db.is_target_state(tranid, state)
        assert ret.state == error.SUCCEED, f"is_target_state({tranid}, {state}) failed."
        return ret.datas

    def exec_refund(self, data, from_sender):
        amount          = int(data["amount"]) 
        tran_id         = data["tran_id"]
        stable_token_id = data["token_id"]
        payee           = data["address"]
        version         = data["version"]

        if self.is_target_state(tran_id, localdb.state.SSUCCEED.value) or \
               self.is_target_state(tran_id, localdb.state.VSUCCEED.value) or \
               self.is_target_state(tran_id, localdb.state.PSUCCEED.value):
            self._logger.warning(f"found transaction is stopped/paymented. (tran_id = {tran_id})) in db({self.dtype}). not exec_refund, ignore it and process next.")
            return result(error.SUCCEED)
        ##convert to BTC satoshi(100000000satoshi == 1000000vBTC)
        ##libra or violas not convert
        amount = self.amountswap(amount, \
                self.amountswap.amounttype[self.from_chain.upper()], 
                self.from_client.get_decimals(stable_token_id)).amount(self.from_chain, self.from_client.get_decimals(stable_token_id))

        self._logger.debug(f"execute refund({tran_id}, {amount}, {stable_token_id})")
        data = self.from_client.create_data_for_stop(self.from_chain, self.dtype, tran_id, 0, version=version) 
        ret = self.from_client.send_coin(from_sender, payee, amount, stable_token_id, data=data)
        if ret.state != error.SUCCEED:
            self.update_localdb_state_with_check(tran_id, localdb.state.SFAILED, detail = None)
            return ret
        else:
            self.update_localdb_state_with_check(tran_id, localdb.state.SSUCCEED, detail = None)
        return result(error.SUCCEED)

    def reexchange_data_from_failed(self, states):
        try:
            #get all info from db
            self._logger.debug(f"start re exchange failed transaction({[state.name for state in states]})")
            ret = self.get_record_from_localdb_with_state(states)
            if ret.state != error.SUCCEED:
                return ret
            rpcparams = ret.datas
            self.show_load_record_info(rpcparams)

            receivers = self.receivers

            #get map sender from  senders
            ret = self.get_map_sender_account()
            self.check_state_raise(ret, f"not found map sender" + 
                    f"check address and amount")
            map_sender = ret.datas

            combine_account = self.get_property("combine_account")

            for receiver in receivers:
                if not self.work() :
                    break
    
                ret = self.from_wallet.get_account(receiver)
                self.check_state_raise(ret, f"get receiver({receiver})'s account failed.")
                from_sender = ret.datas

                #get old transaction from db, check transaction. 
                #version and receiver is current value
                faileds = rpcparams.get(receiver)
                if faileds is not None:
                    self._logger.debug(f"start exchange failed datas from db. receiver={receiver}")
                    for failed in faileds:
                        if (self.work() == False):
                            break

                        tran_id = failed["tran_id"]
                        times   = failed["times"]
                        state   = localdb.state(failed["state"])
                        detail  = failed["detail"]
                        if detail is None or len(detail) == 0:
                            detail = {}
                        else:
                            detail = json.loads(failed["detail"])
                    
                        ret = self.pserver.get_tran_by_tranid(tran_id)
                        if ret.state != error.SUCCEED or ret.datas is None:
                            self._logger.error(f"get transaction(tran_id = {tran_id}) failed.")
                            continue
        
                        data = ret.datas
                        retry = data.get("times")

                        #refund case: 
                        #   case 1: failed times check(metadata: times > 0 (0 = always))  
                        #   case 2: pre exec_refund is failed
                        if (retry != 0 and retry <= times) or state == localdb.state.SFAILED:
                            ret = self.exec_refund(data, from_sender)
                            if ret.state != error.SUCCEED:
                                self._logger.error(ret.message)
                            continue

                        self.__set_request_funds_account(from_sender, map_sender)
                        ret = self.exec_exchange(data, from_sender, map_sender, \
                                self.combine_account, receiver, state = state, detail = detail)
                        if ret.state != error.SUCCEED:
                            self._logger.error(ret.message)

            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret 

    def check_syncing(self, secs = 1):
        if not stmanage.get_syncing_state():
            self._logger.debug(f"syncing closed. ")
            return True

        ret = self.from_client.get_latest_transaction_version()
        assert ret.state == error.SUCCEED, f"check syncing({self.dtype}) failed."
        if ret.state != error.SUCCEED:
            return False
        chain_ver = ret.datas

        while self.work():
            ret = self.pserver.get_latest_chain_ver()
            assert ret.state == error.SUCCEED, f"check syncing({self.dtype}) failed."
            if ret.state != error.SUCCEED:
                return False
            proof_chain_ver = ret.datas
            if proof_chain_ver < chain_ver:
                self._logger.info(f"waitting {self.dtype} to syncing... . " + \
                        f"current proof version: {proof_chain_ver}, chain ver: {chain_ver}, " + \
                        f"diff ver: {chain_ver - proof_chain_ver}")
                sleep(secs)
            else:
                self._logger.debug(f"syncing ok, {self.dtype} to syncing . " + \
                        f"current proof version: {proof_chain_ver}, chain ver: {chain_ver}, " + \
                        f"diff ver: {chain_ver - proof_chain_ver}")
                return True 
        return False

    def start(self):
    
        try:
            self._logger.debug("start works")
            gas = 1000
            receivers = self.receivers

            #requirement checks
            self.__checks()
            self.open_lock()
    
            #syncing
            if not self.check_syncing():
                return result(error.SUCCEED)

            #db state: FAILED
            #if history datas is found state = failed, exchange it until succeed
            self._logger.debug(f"************************************************************ 1/5")
            self.reexchange_data_from_failed(self.use_exec_failed_state)
    
            #db state: SUCCEED
            #check state from blockchain, and change exchange history data, 
            ##when change it to complete, can truncature history db
            self._logger.debug(f"************************************************************ 2/5")
            self.rechange_db_state(self.use_exec_update_db_states)

            #get map sender from senders
            ret = self.get_map_sender_account()
            self.check_state_raise(ret, f"not found map sender. check address")
            map_sender = ret.datas

            #modulti receiver, one-by-one
            self._logger.debug(f"************************************************************ 3/5")
            for receiver in receivers:
                if not self.work() :
                    break

                ret  = self.from_wallet.get_account(receiver)
                self.check_state_raise(ret, f"get receiver({receiver})'s account failed.")
                from_sender = ret.datas
                latest_version = self.latest_version.get(receiver, -1) + 1

                #get new transaction from server
                self._logger.debug(f"start exchange(data type: start), datas from violas server.receiver={receiver}")
                ret = self.pserver.get_transactions_for_start(receiver, self.dtype, latest_version, excluded = self.excluded)
                self._logger.debug(f"will execute transaction(start) : {len(ret.datas)}")
                if ret.state == error.SUCCEED and len(ret.datas) > 0:
                    for data in ret.datas:
                        if not self.work() :
                            break
                        self.__set_request_funds_account(from_sender, map_sender)
                        self.lock()
                        ret = self.exec_exchange(data, from_sender, map_sender, self.combine_account, receiver)
                        self.unlock()
                        if ret.state != error.SUCCEED:
                            self._logger.error(ret.message)

                #get cancel transaction, this version not support
                self._logger.debug(f"start exchange(data type: cancel), datas from violas server.receiver={receiver}")
                ret = self.pserver.get_transactions_for_cancel(receiver, self.dtype, 0, excluded = None)
                self._logger.debug(f"will execute transaction(cancel) count: {len(ret.datas)}")
                if ret.state == error.SUCCEED and len(ret.datas) > 0:
                    for data in ret.datas:
                        if not self.work() :
                            break
                        ret = self.exec_refund(data, from_sender)
                        if ret.state != error.SUCCEED:
                            self._logger.error(ret.message)
    
            #append recover funds(receiver and combine account) to DD account
            self._logger.debug(f"************************************************************ 4/5")

            ret = result(error.SUCCEED) 
            self._logger.debug(f"************************************************************ 5/5")
    
        except Exception as e:
            ret = parse_except(e)
        finally:
            self._logger.debug("works end.")
    
        return ret
    
    '''
    @dev exchange mapping VIOLAS <-> BTC/ETHEREUM
    @param data transaction info from proof db
    @param from_sender receiver account, that receive token from wallet with proof string
    @param combine_account violas account. swap-exchange:receive mapping token, map-exchange: recover funds account
    @param receiver receive token account of update state with end, the same to from_sender's address
    @param state None: new exchange; no-None: last exchange had failed , the state value is obtained from local db
    @param detail cache data during execution
    '''
    def exec_exchange(self, data, from_sender, map_sender, combine_account, receiver, \
            state = None, detail = {}):
        raise Exception("you must be overwrite exec_exchange")

def main():
       print("start main")

if __name__ == "__main__":
    main()
