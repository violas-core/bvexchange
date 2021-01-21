#!/usr/bin/python3
import operator
import sys, os, time
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

class msgmobile(msgbase):    
    def __init__(self, name, 
            proofdb, 
            receivers, 
            senders,
            addressbook,
            fromchain = "violas",
            **kwargs
            ):
        ''' send mobile message (metadata's to_address)
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

        self.append_property("use_exec_update_db_states", 
                [localdb.state.VSUCCEED, localdb.state.SSUCCEED])

    def create_exec_timestamp_key(self, *args):
        return f"_".join([item for item in list(args)])

    def can_send_msg(self, key, sleep_secs):
        ret = self.pserver.get_exec_timestamp(key)
        assert ret.state == error.SUCCEED, "get exec timestamp failed"
        pre_time = ret.datas
        return int(time.time()) - pre_time >= int(sleep_secs)

    def exec_exchange(self, data, receiver, senders, addressbook, \
            state = None, detail = None, min_version = 1):
        version     = data["version"]
        tran_id     = data["tran_id"]
        sender      = data["address"]
        opttype     = data["opttype"]

        #select mobile for opttype or None(receiver all)
        addressbook = [item for item in addressbook if item.get("opttype", opttype) == opttype]

        #filter can send msg, prevent max freq send
        addressbook = [item for item in addressbook if self.can_send_msg(self.create_exec_timestamp_key(item.get("mobile"), opttype), item.get("interval", 3600))]

        self._logger.info(f"start msgmobile {self.dtype}. version={version}, state = {state}, detail = {detail} addressbook = {addressbook} opttype = {opttype} datas from server.")

        #if found transaction in history.db, then get_transactions's latest_version is error(too small or other case)'
        if version < min_version:
            return result(error.ARG_INVALID, f"min version should >= {min_version}")

        if len(addressbook) == 0:
           return result(error.SUCCEED, f"no found mobile had permission receive msg({opttype}). senders({senders})")

        if sender not in senders:
           return result(error.ARG_INVALID, f"sender ({sender}) no permission send msg. senders({senders})")

        if state is None and self.has_info(tran_id):
           return result(error.ARG_INVALID, f"data(version = {version}) is invalid")

        if not self.chain_data_is_valid(data):
           return result(error.ARG_INVALID, f"data(version = {version}) is invalid")

        self._logger.debug(f"exec_exchange-start...")
        if self.use_module(state, localdb.state.START):
            self.insert_to_localdb_with_check(version, localdb.state.START, tran_id, receiver)

        succeed_mobile = json.loads(detail.get("succeed_mobile", json.dumps(["0"])))
        if self.use_module(state, localdb.state.COMPLETE): 
            #send violas map token to payee address. P = payee
            msgdata = self.create_msg_data(data)

            self._logger.debug(f"exec_exchange-1. start send message msgdata = {msgdata} sended succeed mobile = {succeed_mobile}...")

            for item in addressbook:
                mobile = item.get("mobile")
                if mobile in succeed_mobile:
                    self._logger.debug(f"skip {mobile}, next...")
                    continue

                self._logger.debug(f"exec_exchange-2. start from  send {mobile} {msgbase}...")
                ret = self.sms_client.send_message(mobile, msgdata, item.get("lang", "ch"))

                if ret.state != error.SUCCEED:
                    self._logger.error(f"exec_exchange-2.result: failed. {ret.message}")
                    self.update_localdb_state_with_check(tran_id, localdb.state.FAILED, \
                            json.dumps(detail))
                else:
                    self._logger.debug(f"exec_exchange-2.result: succeed. next...")
                    succeed_mobile.append(mobile)
                    detail.update({"succeed_mobile" : json.dumps(succeed_mobile)})
                    self.update_localdb_state_with_check(tran_id, localdb.state.CONTINUE, \
                            json.dumps(detail))

                    self.pserver.set_exec_timestamp(self.create_exec_timestamp_key(mobile, opttype), int(time.time()))


            #check all addressbook is send ok
            complete = True
            for item in addressbook:
                mobile = item.get("mobile")
                if mobile in succeed_mobile:
                    continue
                complete = False

            if complete:
                self.update_localdb_state_with_check(tran_id, localdb.state.COMPLETE, \
                            json.dumps(detail))

        self._logger.debug(f"exec_exchange-end...")
        return result(error.SUCCEED)

