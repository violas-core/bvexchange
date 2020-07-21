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
import requests
import comm
import comm.error
import comm.result
import comm.values
from comm.result import result, parse_except
from comm.error import error
from comm.functions import split_full_address
from db.dbb2v import dbb2v
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
#from .models import BtcRpc
from baseobject import baseobject
from enum import Enum
from btc.violasproxy import violasproxy

#module name
name="bclient"

#btc_url = "http://%s:%s@%s:%i"

COINS = int(comm.values.COINS * (100000000/comm.values.COINS))
class btcclient(baseobject):

    class transaction(object):
        def __init__(self, datas):
            self.__datas = dict(datas)
        def get_version(self):
            return self.__datas.get("version")
        def to_json(self):
            return self.__datas
        def get_events(self):
            return None
        def get_data(self):
            return ""
        def get_token_id(self):
            return "BTC"
        def get_currency_code(self):
            return "BTC"

    class proofstate(Enum):
        START   = "start"
        END     = "end"
        CANCEL  = "cancel"
        STOP    = "stop"
        MARK    = "mark"

    def __init__(self, name, btc_conn):
        self.__btc_url            = "http://%s:%s@%s:%i"
        self.__user               = "btc"
        self.__password           = "btc"
        self.__host               = "127.0.0.1"
        self.__port               = 9409
        self.__rpc_connection        = ""
        baseobject.__init__(self, name)

        if btc_conn :
            self.__user = btc_conn.get("user")
            self.__password = btc_conn.get("password")
            self.__host = btc_conn.get("host")
            self.__port = btc_conn.get("port")
            self.__domain = btc_conn.get("domain")
            server = btc_conn.get("server", "btc")

        self._logger.debug("connect btc server(user={}, password={}, host={}, port={})".format(self.__user, self.__password, self.__host, self.__port))
        if server == "btc":
            self.__rpc_connection = AuthServiceProxy(self.__btc_url%(self.__user, self.__password, self.__host, self.__port))
        else:
            self.__rpc_connection = violasproxy(name, self.__host, self.__port, self.__user, self.__password, self.__domain)
        self._logger.debug(f"connection succeed.")

    def disconn_node(self):
        pass

    def stop(self):
        self.disconn_node()

    def __listexproofforstate(self, opttype, state, extype, receiver, excluded):
        try:
            self._logger.debug(f"start __listexproofforstate(opttype = {opttype} state={state} type={extype} receiver={receiver} excluded={excluded})")
            if(len(receiver) == 0):
                return result(error.ARG_INVALID, error.argument_invalid, "")
            
            if excluded is None or len(excluded) == 0:
                datas = self.__rpc_connection.violas_listexproofforstate(opttype, state, extype, receiver)
            else:
                datas = self.__rpc_connection.violas_listexproofforstate(opttype, state, extype, receiver, excluded)

            ret = result(error.SUCCEED, "", datas)
            self._logger.info(f"result: {len(ret.datas)}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def stop(self):
        self.work_stop()

    def __listexproof(self, extype, cursor = 0, limit = 10):
        try:
            self._logger.debug(f"start __listexproof(type={extype} cursor={cursor} limit={limit})")
            
            datas = self.__rpc_connection.violas_listexproof(extype, cursor, limit)

            ret = result(error.SUCCEED, "", datas)
            self._logger.info(f"result: {len(ret.datas)}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def isexproofcomplete(self, opttype, address, sequence):
        try:
            self._logger.debug(f"start isexproofcomplete(opttype={opttype} address = {address} sequence={sequence})")
            if(len(address) != 64 or sequence < 0):
                return result(error.ARG_INVALID, error.argument_invalid, "")
                
            datas = self.__rpc_connection.violas_isexproofcomplete(opttype, address, sequence)
            ret = result(error.SUCCEED, "", datas)
            self._logger.debug(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_transaction(self, tranid):
        try:
            datas = self.__rpc_connection.violas_gettransaction(tranid)
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_transactions_for_start(receiver, opttype, start_version = None):
        return self.__listexproofforstate(opttype, self.proofstate.START.value, comm.values.EX_TYPE_PROOF, receiver, excluded)

    def listexproofforstart(self, opttype, receiver, excluded):
        return self.__listexproofforstate(opttype, self.proofstate.START.value, comm.values.EX_TYPE_PROOF, receiver, excluded)

    def listexproofforend(self, opttype, receiver, excluded):
        return self.__listexproofforstate(opttype, self.proofstate.END.value, comm.values.EX_TYPE_PROOF, receiver, excluded)

    def get_transactions_for_cancel(receiver, opttype, start_version, excluded = None):
        return self.__listexproofforstate(opttype, self.proofstate.CANCEL.value, comm.values.EX_TYPE_PROOF, receiver, excluded)

    def listexproofforcancel(self, opttype, receiver, excluded):
        return self.__listexproofforstate(opttype, self.proofstate.CANCEL.value, comm.values.EX_TYPE_PROOF, receiver, excluded)

    def listexproofforstop(self, opttype, receiver, excluded):
        return self.__listexproofforstate(opttype, self.proofstate.STOP.value, comm.values.EX_TYPE_PROOF, receiver, excluded)

    def listexproofformark(self, opttype, receiver, excluded):
        return self.__listexproofforstate(opttype, self.proofstate.MARK.value, comm.values.EX_TYPE_MARK, receiver, excluded)

    def listexproofforb2v(self, cursor, limit):
        return self.__listexproof(comm.values.EX_TYPE_PROOF, cursor, limit)

    def __map_tran(self, data):
        tran_data = json.dumps({"flag":"btc", \
            "type":"b2v", "state":data.get("state"), "to_address":data.get("address"), "to_module":data.get("vtoken"), \
            "out_ampunt":data.get("out_amount"), "times":data.get("times"), "tran_id":data.get("txid"), \
            "sequence":data.get("sequence")})
        _, module = split_full_address(data.get("vtoken"))
        return {
                "version": data.get("index"),\
                "success":True,\
                "events":[{"event":tran_data}],\
                "data":tran_data.encode("utf-8").hex(),\
                "amount":int(data.get("amount") * COINS),\
                "sequence_number":data.get("height"),\
                "txid":data.get("txid"),\
                "tran_id":data.get("txid"),\
                "creation_block":data.get("creation_block"),\
                "update_block":data.get("update_block"),\
                "sender":data.get("issuer"), \
                "receiver":data.get("receiver"),\
                "module_address":module \
                }

    def get_tran_by_tranid(self, tran_id):
        try:
            ret = self.get_transaction(tran_id)
            if ret.state != error.SUCCEED:
                return ret

            tran = self.__map_tran(ret.datas)
            if tran["data"] is not None:
                del tran["data"]
            ret = result(error.SUCCEED, "", tran)
            self._logger.debug(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret


    def get_transactions(self, cursor, limit = 1, nouse=True):
        try:
            ret = self.listexproofforb2v(cursor, limit)
            if ret.state != error.SUCCEED:
                return ret
            datas = []
            for data in ret.datas:
                tran = self.__map_tran(data)
                datas.append(self.transaction(tran))
            ret = result(error.SUCCEED, "", datas)
            self._logger.debug(f"result: {len(ret.datas)}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_latest_transaction_version(self):
        try:
            latest_index = self.__rpc_connection.violas_getexprooflatestindex(comm.values.EX_TYPE_PROOF)
            ret = result(error.SUCCEED, "", int(latest_index))
            self._logger.debug(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def sendexproofstart(self, opttype, fromaddress, toaddress, amount, vaddress, sequence, vtoken):
        try:
            self._logger.info(f"start sendexproofstart (opttype={opttype}, fromaddress={fromaddress}, toaddress={toaddress}, amount={amount:.8f}, vaddress={vaddress}, sequence={sequence}, vtoken={vtoken})")
            datas = self.__rpc_connection.violas_sendexproofstart(opttype, fromaddress, toaddress, f"{amount:.8f}", vaddress, sequence, vtoken)
            ret = result(error.SUCCEED, "", datas)
            self._logger.info(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def create_data_for_end(self, flag, opttype, tranid, version):
        address_seq = tranid.split("_")
        return {"type": "end", "flag": flag, "opttype":opttype, "address":address_seq[0], \
                "sequence":address_seq[1], "version":version}

    def create_data_for_end(self, flag, opttype, tranid, version):
        address_seq = tranid.split("_")
        return {"type": "stop", "flag": flag, "opttype":opttype, "address":address_seq[0], \
                "sequence":address_seq[1], "version":version}

    def send_coin(fromaddress, toaddress, amount, token_id, data):
        if data["type"] == "end":
            self.sendexproofend(data["opttype"], fromaddress, toaddress, data["address"], \
                    data["sequence"], data["amount"], data["version"])
        elif data["type"] == "stop":
            self.sendexproofstop(data["opttype"], fromaddress, toaddress, amount, data["address"], \
                    data["sequence"])


    def sendexproofend(self, opttype, fromaddress, toaddress, vaddress, sequence, amount, version):
        try:
            self._logger.info(f"start sendexproofend (opttype={opttype}, fromaddress={fromaddress},"+
                    f" toaddress={toaddress}, vaddress={vaddress}, sequence={sequence}, " +
                    f"amount={amount:.8f}, version={version})")

            datas = self.__rpc_connection.violas_sendexproofend(opttype, \
                    fromaddress, toaddress, vaddress, sequence, f"{amount:.8f}", version)

            ret = result(error.SUCCEED, "", datas)
            self._logger.info(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def sendexproofstop(self, opttype, fromaddress, toaddress, amount, vaddress, sequence):
        try:
            self._logger.info(f"start sendexproofstop(opttype={opttype}, fromaddress={fromaddress},"+
                    f" toaddress={toaddress}, amount = {amount}, vaddress={vaddress}, " + 
                    f"sequence={sequence})")

            datas = self.__rpc_connection.violas_sendexproofstop(opttype, \
                    fromaddress, toaddress, amount, vaddress, sequence)

            ret = result(error.SUCCEED, "", datas)
            self._logger.info(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def sendtoaddress(self, address, amount):
        try:
            self._logger.info(f"start sendtoaddress(address={address}, amount={amount})")
            datas = self.__rpc_connection.sendtoaddress(address, f"{amount:.8f}")
            ret = result(error.SUCCEED, "", datas)
            self._logger.info(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret
   
    def sendexproofmark(self, fromaddress, toaddress, toamount, vaddress, sequence, version):
        try:
            self._logger.info(f"start sendexproofmark(fromaddress={fromaddress}, " + 
                    f"toaddress={toaddress}, toamount={toamount:.8f}, vaddress={vaddress}, " + 
                    f"sequence={sequence}, version={version})")

            datas = self.__rpc_connection.violas_sendexproofmark(fromaddress, toaddress, \
                    f"{toamount:.8f}", vaddress, sequence, version)

            ret = result(error.SUCCEED, "", datas)
            self._logger.info(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def generatetoaddress(self, count, address):
        try:
            self._logger.info(f"start generatetoaddress(count={count}, address={address})")
            datas = self.__rpc_connection.generatetoaddress(count, address)
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def listunspent(self, minconf = 1, maxconf = 9999999, addresses = None, \
            include_unsafe = True, query_options = None):
        try:
            self._logger.debug(f"start listunspent(minconf={minconf}, maxconf={maxconf}, " + 
                    f"addresses={addresses}, include_unsafe={include_unsafe}, " + 
                    f"query_options={query_options})")

            datas = self.__rpc_connection.listunspent(minconf, maxconf, \
                    addresses, include_unsafe, query_options)

            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def help(self):
        try:
            self._logger.debug("start help")
            datas = self.__rpc_connection.help()
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def getwalletbalance(self):
        try:
            self._logger.debug("start getwalletbalance")
            walletinfo = self.__rpc_connection.getwalletinfo()
            balance = walletinfo.get("balance", 0)
            ret = result(error.SUCCEED, "", balance)
            self._logger.debug(f"result: {ret.datas:.8f}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_balance(address, token_id = None):
        return self.getwalletbalance(address)

    def getwalletaddressbalance(self, address):
        try:
            self._logger.debug(f"start getwalletaddressbalance({address})")
            addresses = [address]
            datas = self.__rpc_connection.listunspent(1, 999999999, addresses)
            balance = 0
            if len(datas) == 0:
                return result(error.FAILED)
            for data in datas:
                balance += data.get("amount", 0)

            ret = result(error.SUCCEED, "", balance)
            self._logger.debug(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def has_btc_banlance(self, address, vamount, gas = comm.values.MIN_EST_GAS):
        try:
            self._logger.debug(f"start has_btc_banlance(address={address}, vamount={vamount}, gas={gas})")
            ret = self.getwalletaddressbalance(address)
            if ret.state != error.SUCCEED:
                return ret
    
            #change bitcoin unit to satoshi and check amount is sufficient
            wbalance = int(ret.datas * comm.values.COINS)
            if wbalance <= (vamount + gas): #need some gas, so wbalance > vamount
                ret = result(error.SUCCEED, "", False)
            else:
                ret = result(error.SUCCEED, "", True)
            self._logger.debug(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret


def main():
    try:
       #load logging
       pass

    except Exception as e:
        parse_except(e)
    finally:
        print("end main")

if __name__ == "__main__":
    main()
