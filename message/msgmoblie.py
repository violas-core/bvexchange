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
from message.msgbase import msgbase

class msgmoblie(msgbase):    
    def __init__(self, name, 
            proofdb, 
            receivers, 
            senders,
            addressbook,
            fromchain,
            **kwargs
            ):
        ''' send moblie message (metadata's to_address)
            proofdb  : transaction proof source(proof db conf)
            receivers: receive msg requests address
            senders: sender of permission to send message 
            addressbook  : addressbook of receiver message
            fromchain: source chain name
            kwargs:
                sms_nodes: connect sms node info
                sms_templetes: sms templetes
                sms_lang: use templete
                funds_receiver: mint or recharge address
        '''


        msgbase.__init__(self, name, \
                proofdb, receivers, senders, addressbook, \
                fromchain, \
                **kwargs)
        self.init_exec_states()

    def __del__(self):
        pass

    def init_exec_states(self):
        self.append_property("use_exec_failed_state", 
            [state for state in localdb.state \
                    if state not in [localdb.state.COMPLETE, \
                        localdb.state.VSUCCEED, \
                        localdb.state.SSUCCEED]])

    def exec_exchange(self, data, receiver, senders, addressbook, \
            state = None, detail = {}, min_version = 1):
        version     = data["version"]
        tran_id     = data["tran_id"]
        sender      = data["address"]

        self._logger.info(f"start exfunds {self.dtype}. version={version}, state = {state}, detail = {detail} datas from server.")

        #if found transaction in history.db, then get_transactions's latest_version is error(too small or other case)'
        if version < min_version:
            return result(error.ARG_INVALID, f"min version should >= {min_version}")

        if sender not in senders:
           return result(error.ARG_INVALID, f"sender ({sender}) no permission send msg.")

        if state is None and self.has_info(tran_id):
           return result(error.ARG_INVALID, f"data(version = {version}) is invalid")

        if not self.chain_data_is_valid(data):
           return result(error.ARG_INVALID, f"data(version = {version}) is invalid")

        self._logger.debug(f"exec_exchange-start...")
        if self.use_module(state, localdb.state.START):
            self.insert_to_localdb_with_check(version, localdb.state.START, tran_id, receiver)

        if self.use_module(state, localdb.state.COMPLETE): 
            succeed_moblie = detail.get("succeed_moblie", [])

            #send violas map token to payee address. P = payee
            msgdata = self.create_msg_data(data)

            self._logger.debug(f"exec_exchange-1. start send message msgdata = {msgdata} sended succeed moblie = {succeed_moblie}...")

            for item in addressbook:
                mobile = item.get("mobile")
                if mobile in succeed_moblie:
                    continue

                self._logger.debug(f"exec_exchange-2. start from  send {mobile} {msgbase}...")
                ret = self.sms_client.send_message(moblie, msgdata, item.get("lang", "ch"))

                if ret.state != error.SUCCEED:
                    self._logger.error(f"exec_exchange-2.result: failed. {ret.message}")
                    self.update_localdb_state_with_check(tran_id, localdb.state.FAILED, \
                            json.dumps(detail))
                else:
                    self._logger.error(f"exec_exchange-2.result: succeed. next...")
                    succeed_moblie.append(mobile)
                    detail.update({"succeed_moblie" : json.dumps(succeed_moblie)})

            #check all addressbook is send ok
            complete = True
            for mobile in addressbook:
                if mobile in succeed_moblie:
                    continue
                complete = False

            if complete:
                self.update_localdb_state_with_check(tran_id, localdb.state.COMPLETE, \
                            json.dumps(detail))

        self._logger.debug(f"exec_exchange-end...")
        return result(error.SUCCEED)

