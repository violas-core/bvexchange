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
from btc.btcclient import btcclient
from btc.btcwallet import btcwallet
from vlsopt.violasproof import violasproof
from baseobject import baseobject
from enum import Enum
from vrequest.request_client import requestclient
from analysis.analysis_filter import afilter
from dataproof import dataproof
from comm.values import (
        trantypebase as trantype,
        datatypebase as datatype, 
        )
from comm.functions import (
        output_args
        )

#load logging
class msgbase(baseobject):    

    class amountswap(amountconver):
        pass

    def __init__(self, name, \
            proofdb, receivers, senders, addressbook, \
            fromchain = trantype.VIOLAS.value, \
            **kwargs):
        ''' swap token and send coin to payee(metadata's to_address)
            proofdb  : transaction proof source(proof db conf)
            receivers: receive msg requests address
            senders: sender of permission to send message 
            addressbook  : addressbook of receiver message
            fromchain: source chain name
            kwargs:
                sms_nodes: connect sms node info
                sms_templetes: sms templetes
                sms_lang: use templete
                min_version: min version of message
        '''

        baseobject.__init__(self, name)
        self.from_chain = self.to_str(from_chain)
    
        #violas/libra init
        self.append_property("receivers", receivers)
        self.append_property("addressbook", addressbook)
        self.append_property("dtype", datatype.MSG.value)
        self.append_property("proofdb", proofdb)
        self.append_property("senders", senders)

        #use the above property, so call set_local_workspace here
        self.set_local_workspace(**kwargs)

        self.show_execute_args(name, self.dtype, \
                proofdb, receivers, senders, \
                fromchain, **kwargs)

    def __del__(self):
        pass

    def set_local_workspace(self, **kwargs):

        self.append_property("min_version", int(kwargs.get("min_version", 1)))
        self.append_property("pserver", requestclient(self.name(), self.proofdb))
        self.append_property(f"{self.from_chain}_chain", self.from_chain)
        self.append_property("db", localdb(self.name(), f"{self.from_chain}_{self.dtype}.db"))
        #block chain 
        ttype = trantype(self.from_chain)
        chain_nodes = kwargs.get(self.create_nodes_key(ttype))
        self.append_property(self.create_client_key(ttype)), \
                clientfactory.create(self.name(), ttype, chain_nodes)
        
        self.append_property("from_client", self.get_property(self.create_nodes_key(ttype)))

        #sms client
        ttype = trantype(trantype.SMS)
        chain_nodes = kwargs.get(self.create_nodes_key(ttype))
        self.append_property(self.create_client_key(ttype), \
                clientfactory.create(self.name(), ttype, chain_nodes, \
                    templetes = kwargs.get("templetes"), lang = kwargs.get("lang")))
        

    def show_execute_args(self, name, dtype, \
            proofdb, receivers, senders, \
            fromchain, \
            **kwargs):
        if dataproof.configs("help_exe_args"):
            self._logger.debug(
            f'''
            name = {name}
            dtype = {dtype}
            proofdb = {proofdb}
            receivers = {receivers}
            fromchain : {fromchain}
            kwargs = {kwargs}
            ''')

    def is_end(self, tran_id):
        return self.pserver.is_end(tran_id)

    def is_stop(self, tran_id):
        return self.pserver.is_stop(tran_id)

    def use_module(self, state, module_state):
        return state is None or state.value < module_state.value

    def has_info(self, tranid):
        ret = self.db.has_info(tranid)
        assert ret.state == error.SUCCEED, f"has_info({tranid}) failed."
        if ret.datas == True:
            self._logger.warning(f"found transaction(tran_id = {tranid})) in db(maybe first run {self.dtype}). " + 
                    f"ignore it and process next.")
        return ret.datas

    def create_msg_data(self, data):
        SPLIT_SYMBOL = ":"
        fields = ["opttype", "flag", "token_id", "amount", "version"]
        return f"{SPLIT_SYMBOL}".join([data.get(field) for field in fields])


    # local db state is VSUCCEED , update state to COMPLETE
    def rechange_db_state(self, states):
        try:
            ##update violas blockchain state to end, if sendexproofmark is ok
            self._logger.debug(f"start rechange_db_state({[state.name[0] for state in states]})")
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

    def reexchange_data_from_failed(self, states):
        try:
            #get all info from db
            self._logger.debug(f"start re exchange failed transaction({[state.name[0] for state in states]})")
            ret = self.get_record_from_localdb_with_state(states)
            if ret.state != error.SUCCEED:
                return ret
            rpcparams = ret.datas
            self.show_load_record_info(rpcparams)

            receivers = self.receivers

            for receiver in receivers:
                if not self.work() :
                    break

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

                        ret = self.exec_exchange(data, receiver, self.addressbook, state = state, detail = detail, min_version = self.min_version)
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
            self.open_lock(dataproof.configs("exchange_async"))
    
            #syncing
            if not self.check_syncing():
                return result(error.SUCCEED)

            self.lock()
            #db state: FAILED
            #if history datas is found state = failed, exchange it until succeed
            self._logger.debug(f"************************************************************ 1/5")
            self.reexchange_data_from_failed(self.use_exec_failed_state)
    
            #db state: SUCCEED
            #check state from blockchain, and change exchange history data, 
            ##when change it to complete, can truncature history db
            self._logger.debug(f"************************************************************ 2/5")
            self.rechange_db_state(self.use_exec_update_db_states)

            #modulti receiver, one-by-one
            self._logger.debug(f"************************************************************ 3/5")
            for receiver in receivers:
                if not self.work() :
                    break

                latest_version = self.pserver.get_exec_points(receiver).datas + 1

                #get new transaction from server
                self._logger.debug(f"start exchange(data type: start), datas from violas server.receiver={receiver} start version = {latest_version}")
                ret = self.pserver.get_transactions_for_start(receiver, self.dtype, latest_version, excluded = self.excluded)
                self._logger.debug(f"will execute transaction(start) : count: {len(ret.datas)}")
                if ret.state == error.SUCCEED and len(ret.datas) > 0:
                    for data in ret.datas:
                        if not self.work() :
                            break

                        self.pserver.set_exec_points(receiver, max(latest_version, int(data.get("version"))))
                        ret = self.exec_exchange(data, receiver, self.senders, self.addressbook, min_version = self.min_version)
                        if ret.state != error.SUCCEED:
                            self._logger.error(ret.message)


            ret = result(error.SUCCEED) 
            self._logger.debug(f"************************************************************ 4/5")
    
        except Exception as e:
            ret = parse_except(e)
        finally:
            self.unlock()
            self._logger.debug("works end.")
    
        return ret
    
    def exec_exchange(self, data, receiver, senders, addressbook, state = None, detail = {}, min_version = 1):
        '''
        @dev exchange mapping VIOLAS <-> BTC/ETHEREUM
        @param data transaction info from proof db
        @param receiver receive token account of update state with end, the same to from_sender's address
        @param senders sender of permission to send message 
        @param addressbook receive message addressbook
        @param state None: new exchange; no-None: last exchange had failed , the state value is obtained from local db
        @param detail cache data during execution
        '''
        raise Exception("you must be overwrite exec_exchange")