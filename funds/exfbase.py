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
from wallet_factory import walletfactory
from client_factory import clientfactory
from time import sleep
from comm.result import result, parse_except
from comm.error import error
from comm.amountconver import amountconver 
from db.dblocal import dblocal as localdb
from baseobject import baseobject
from vrequest.request_client import requestclient
from comm.values import datatypebase as datatype, trantypebase as trantype
from dataproof import dataproof

#module self.name
#name="exfbase"

VIOLAS_ADDRESS_LEN = comm.values.VIOLAS_ADDRESS_LEN
#load logging
class exfbase(baseobject):    
    PRE_FIX = "funds"

    class amountswap(amountconver):
        pass

    def __init__(self, name, dtype, \
            proofdb, receivers, \
            fromchain = "violas", \
            tochain = "violas", \
            **kwargs):
        ''' swap token and send coin to payee(metadata's to_address)
            proofdb  : transaction proof source(proof db conf)
            receivers: addresses of receive funds request 
            fromchain: source chain name: violas
            tochain: target chain name: violas btc ethereum libra
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

        baseobject.__init__(self, name)
        self.from_chain = fromchain
        self.to_chain = tochain
        self.excluded = None

        self.append_property("db", localdb(name, f"funds_{self.from_chain}_{self.to_chain}_{dtype}.db"), path = dataproof.configs("datas_root_path"))
    
        #violas/libra init
        self.append_property("receivers", receivers)
        self.append_property("dtype", dtype)
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
        self.append_property("pserver", requestclient(self.name(), self.proofdb))
        self.append_property("request_funds_sender", kwargs.get("request_funds_sender"))

        for ttype in trantype:
            if ttype == trantype.UNKOWN:
                continue
            senders_name = self.create_senders_key(ttype.value)

            arg_senders_name = kwargs.get(senders_name)
            arg_chain_nodes = kwargs.get(self.create_nodes_key(ttype.value))

            #set property for senders 
            self.append_property(senders_name, arg_senders_name)

            if arg_senders_name and arg_chain_nodes:
                #set property for wallet
                self.append_property(self.create_wallet_key(ttype.value), \
                        walletfactory.create(self.name(), ttype.value))

                #set property for client
                self.append_property(self.create_client_key(ttype.value), \
                        clientfactory.create(self.name(), ttype.value, arg_chain_nodes))
            else:
                self.append_property(self.create_wallet_key(ttype.value), None) 
                self.append_property(self.create_client_key(ttype.value), None)



    def load_vlsmproof(self, address):
        if self.ethereum_client:
            self.ethereum_client.load_vlsmproof(address)

    def has_request_funds_permission(self, address):
        return address in self.request_funds_sender

    def append_contract(self, name):
        if self.ethereum_client:
            self.ethereum_client.load_contract(name)

    def insert_to_localdb_with_check(self, version, state, tran_id, receiver, detail = json.dumps({"default":"no-use"})):
        ret = self.db.insert_commit(version, state, tran_id, receiver, detail)
        assert (ret.state == error.SUCCEED), "db error"
        return ret

    def update_localdb_state_with_check(self, tran_id, state, detail = json.dumps({"default":"no-use"})):
        ret = self.db.update_state_commit(tran_id, state, detail = detail)
        assert (ret.state == error.SUCCEED), "db error"
        return ret

    def get_map_sender_account(self, chain, token_id, amount):
        try:
            sender_account = None
            senders_name = self.create_senders_key(chain)
            map_wallet = self.get_property(self.create_wallet_key(chain))
            senders = self.get_property(senders_name)
            for sender in senders:
                ret = map_wallet.get_account(sender)
                if ret.state != error.SUCCEED:
                    continue
                sender_account = ret.datas

                ret = self.check_address_token_is_enough(self.get_property(self.create_client_key(chain)),
                        sender_account, token_id, amount
                        )
                if ret.state != error.SUCCEED:
                    continue

                if not ret.datas:
                    continue

                return result(error.SUCCEED, datas = sender_account)

            return result(error.FAILED, f"request funds amount({amount}{token_id}) from {senders} is too big" if len(senders) > 0 else "not found sender account " )
        except Exception as e:
            ret = parse_except(e)
        return ret

    def check_address_token_is_enough(self, client, account, token_id, amount):
        try:
            address = self.get_address_from_account(account)
            ret = client.get_balance(address, token_id = token_id)
            assert ret.state == error.SUCCEED, f"get balance failed"
            
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

    def get_record_from_localdb_with_state(self, states):
        try:
            maxtimes = stmanage.get_max_times()
            ret = self.db.get_record_from_localdb_with_state(states, maxtimes)
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
            self._logger.debug(f"record info:{self.db.format_record_info(rpcparams)}")
            
            for key in rpcparams.keys():
                datas = rpcparams.get(key)
                for data in datas:
                    tran_id = data.get("tran_id")
                    if tran_id is None:
                        continue
                    ret = self.pserver.is_end(tran_id)
                    if ret.state == error.SUCCEED and ret.datas == True:
                       ret = self.update_localdb_state_with_check(tran_id, localdb.state.COMPLETE, detail = None)

                    ret = self.pserver.is_stop(tran_id)
                    if ret.state == error.SUCCEED and ret.datas == True:
                       ret = self.update_localdb_state_with_check(tran_id, localdb.state.COMPLETE, detail = None)

        except Exception as e:
            ret = parse_except(e)
        return ret

    def send_coin_for_update_state_to_end(self, sender, receiver, tran_id, vls_token_id, amount = 1, **kwargs):
            self._logger.debug(f"start send_coin_for_update_state_to_end(sender={sender},"\
                    f"recever={receiver}, tran_id={tran_id}, amount={amount})")
            tran_data = self.violas_client.create_data_for_end(self.from_chain, self.dtype, tran_id, **kwargs)
            ret = self.violas_client.send_coin(sender, receiver, amount, vls_token_id, data = tran_data)
            if ret.state != error.SUCCEED:
                self.update_localdb_state_with_check(tran_id, localdb.state.VFAILED, detail = None)
            else:
                self.update_localdb_state_with_check(tran_id, localdb.state.VSUCCEED, detail = None)
            return ret

    def __checks(self):
        return True
    
    def chain_data_is_valid(self, data):
        if False: # btc and violas is diff ????????
            self._logger.warning(f"transaction(tran_id = {data['tran_id']})) is invalid. " + 
                    f"ignore it and process next.")
            return False
        return True

    def has_info(self, tranid):
        ret = self.db.has_info_with_assert(tranid)
        return ret

    def reexchange_data_from_failed(self, states):
        try:
            #get all info from db
            self._logger.debug(f"start re exchange failed transaction({[state.name[0] for state in states]})")
            ret = self.get_record_from_localdb_with_state(states)
            if ret.state != error.SUCCEED:
                return ret
            rpcparams = ret.datas
            self._logger.debug(f"record info:{self.db.format_record_info(rpcparams)}")

            receivers = self.receivers


            for receiver in receivers:
                if not self.work() :
                    break
    
                ret = self.violas_wallet.get_account(receiver)
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
                        chain = data.get("chain")
                        token_id = data.get("token_id")
                        amount = data.get("amount")
                        sender = data.get("address")

                        if not self.has_request_funds_permission(sender):
                            self._logger.debug(f"sender not permission to request funds")
                            continue

                        #get map sender from  senders
                        #if token amount is too small, exchange next request, until funds account can payment token to requestor
                        #Reprocessing error logic is different from main logic ----**********----
                        ret = self.get_map_sender_account(chain, token_id, amount)
                        if ret.state != error.SUCCEED:
                            self._logger.warning(f"get map sender failed(chain = {chain}  token_id={token_id} amount={amount}). " + 
                                f"{ret.message}")
                            continue

                        map_sender = ret.datas

                        #refund case: 
                        #   case 1: failed times check(metadata: times > 0 (0 = always))  
                        if retry != 0 and retry <= times:
                            continue

                        ret = self.exec_exchange(data, from_sender, map_sender, \
                                receiver, state = state, detail = detail)
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

        ret = self.violas_client.get_latest_transaction_version()
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
            receivers = self.receivers

            #requirement checks
            self.__checks()
    
            #syncing
            if not self.check_syncing():
                return result(error.SUCCEED)

            #db state: FAILED
            #if history datas is found state = failed, exchange it until succeed
            self._logger.debug(f"************************************************************ 1/4")
            self.reexchange_data_from_failed(self.use_exec_failed_state)
    
            #db state: SUCCEED
            #check state from blockchain, and change exchange history data, 
            ##when change it to complete, can truncature history db
            self._logger.debug(f"************************************************************ 2/4")
            self.rechange_db_state(self.use_exec_update_db_states)


            #modulti receiver, one-by-one
            self._logger.debug(f"************************************************************ 3/4")
            for receiver in receivers:
                if not self.work() :
                    break

                ret  = self.violas_wallet.get_account(receiver)
                self.check_state_raise(ret, f"get receiver({receiver})'s account failed.")
                from_sender = ret.datas
                latest_version = self.pserver.get_exec_points(receiver, self.PRE_FIX).datas + 1

                #get new transaction from server
                self._logger.debug(f"start exchange(data type: start), datas from violas server.receiver={receiver}")
                ret = self.pserver.get_transactions_for_start(receiver, self.dtype, latest_version, excluded = self.excluded)
                self._logger.debug(f"will execute transaction(start) : {len(ret.datas)}")
                if ret.state == error.SUCCEED and len(ret.datas) > 0:
                    for data in ret.datas:
                        if not self.work() :
                            break

                        #get map sender from senders, chain and token_id is multi
                        chain = data.get("chain")
                        token_id = data.get("token_id")
                        amount = data.get("amount")
                        sender = data.get("address")
                        version = data.get("version")

                        if not self.has_request_funds_permission(sender):
                            self.pserver.set_exec_points(receiver, max(latest_version,version), self.PRE_FIX)
                            self._logger.debug(f"sender not permission to request funds")
                            continue

                        #get map sender from  senders
                        #if token's amount is too small, not exchange next version
                        #set amount = 1, maybe next request amount is enough
                        ret = self.get_map_sender_account(chain, token_id, 1) #amount
                        self.check_state_raise(ret, f"get map sender failed(chain = {chain}  token_id={token_id} amount={amount}).")
                        map_sender = ret.datas

                        self.pserver.set_exec_points(receiver, max(latest_version,version), self.PRE_FIX)
                        ret = self.exec_exchange(data, from_sender, map_sender, receiver, None, {})
                        if ret.state != error.SUCCEED:
                            self._logger.error(ret.message)
    
            ret = result(error.SUCCEED) 
            self._logger.debug(f"************************************************************ 4/4")
    
        except Exception as e:
            ret = parse_except(e)
        finally:
            self._logger.debug("works end.")
    
        return ret
    
def main():
       print("start main")

if __name__ == "__main__":
    main()
