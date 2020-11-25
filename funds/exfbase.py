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

#module self.name
#name="exfbase"

VIOLAS_ADDRESS_LEN = comm.values.VIOLAS_ADDRESS_LEN
#load logging
class exfbase(baseobject):    

    class amountswap(amountconver):
        pass

    def __init__(self, name, dtype, \
            proofdb, receivers, \
            fromchain = "violas", \
            **kwargs):
        ''' swap token and send coin to payee(metadata's to_address)
            proofdb  : transaction proof source(proof db conf)
            receivers: receive chain' addresses
            fromchain: source chain name: violas
            kwargs:
                btc_nodes: connect btc node info
                violas_nodes: connect violas node info
                libra_nodes: connect libra node info
                ethereum_nodes: connect ethereum node info
                btc_senders: btc chain accounts
                violas_senders: violas chain accounts
                libra_senders: libra chain accounts
                ethereum_senders: ethereum chain accounts
        '''

        baseobject.__init__(self, name)
        self.latest_version = {}
        self.from_chain = fromchain
        self.excluded = None

        self.append_property("db", localdb(name, f"{self.from_chain}_{dtype}.db"))
    
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

    def load_vlsmproof(self, address):
        if self.ethereum_client:
            self.ethereum_client.load_vlsmproof(address)

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
                    self._logger.debug(f"account({sender})'s token({token_id}) amount < request amount({amount})")
                    continue

                return result(error.SUCCEED, datas = sender_account)

            return result(error.FAILED, "not found sender account or amount({amount}) is too big")
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
            maxtimes = stmanage.get_max_times(self.name())

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
            tran_data = self.violas_client.create_data_for_end(self.from_chain, self.dtype, tran_id, **kwargs)
            ret = self.violas_client.send_coin(sender, receiver, amount, token_id, data = tran_data)
            if ret.state != error.SUCCEED:
                self.update_localdb_state_with_check(tran_id, localdb.state.VFAILED, detail = None)
            else:
                self.update_localdb_state_with_check(tran_id, localdb.state.VSUCCEED, detail = None)
            return ret

    def __checks(self):
        return True
    
    def get_address_from_account(self, account):
        if not isinstance(account, str):
            address = account.address
            if not isinstance(address, str):
                address = address.hex()
        else:
            address = account
        return address

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

                        #get map sender from  senders
                        ret = self.get_map_sender_account(chain, token_id, amount)
                        self.check_state_raise(ret, f"not found {chain} {token_id} map sender or request amount is too big, " + 
                                f"check address and amount({amount})")
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
            gas = 1000
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
                latest_version = self.latest_version.get(receiver, -1) + 1

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

                        #get map sender from  senders
                        ret = self.get_map_sender_account(chain, token_id, amount)
                        self.check_state_raise(ret, f"not found {chain} {token_id} map sender, " + 
                                f"check address and amount({amount})")
                        map_sender = ret.datas

                        ret = self.exec_exchange(data, from_sender, map_sender, receiver)
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
