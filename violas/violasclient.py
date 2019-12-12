#!/usr/bin/python3
import operator
import sys
import json
import os
sys.path.append("..")
sys.path.append("../packages")
import libra
from libra import Client
from libra import WalletLibrary
from libra.json_print import json_print
import log
import log.logger
import traceback
import datetime
import sqlalchemy
import setting
import requests
import random
import comm
import comm.error
import comm.result
from comm.result import result
from comm.error import error
from db.dbb2v import dbb2v
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from enum import Enum

#module name
name="violasclient"

#load logging
logger = log.logger.getLogger(name) 

class violaswallet:
    __traceback_limit       = 0
    __wallet_name           = "vwallet"
    
    def __init__(self, traceback_limit, wallet_name):
        self.__traceback_limit = traceback_limit
        assert wallet_name is not None, "wallet_name is None"
        if wallet_name is not None:
            ret = self.__load_wallet(wallet_name)
            if ret.state != error.SUCCEED:
                raise Exception("load wallet failed.")

    def __del__(self):
        self.dump_wallet()

    def __load_wallet(self, wallet_name):
        try:
            logger.debug("start load_wallet({})".format(wallet_name))
            self.__wallet_name = wallet_name
            if os.path.isfile(self.__wallet_name):
                self.__wallet = WalletLibrary.recover(self.__wallet_name)
                #self.__wallet.recover(self.__wallet_name)
                ret = result(error.SUCCEED, "", "")
            else:
                ret = result(error.ARG_INVALID, "not found wallet file", "")
                self.__wallet = WalletLibrary.new()

        except Exception as e:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.EXCEPT, str(e), e)
        return ret

    def dump_wallet(self):
        try:
            logger.debug("start dump_wallet")
            self.__wallet.write_recovery(self.__wallet_name)
            ret = result(error.SUCCEED)
        except Exception as e:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.EXCEPT, str(e), e)
        return ret

    def new_account(self):
        try:
            logger.debug("start new_wallet")
            account = self.__wallet.new_account();
            ret = result(error.SUCCEED, "", account)
        except Exception as e:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.EXCEPT, str(e), e)
        return ret

    def get_account_count(self):
        return self.__wallet.child_count

    def get_account(self, addressorid):
        try:
            account = self.__wallet.get_account_by_address_or_refid(addressorid)
            ret = result(error.SUCCEED, "", account)
        except Exception as e:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.EXCEPT, str(e), e)
        return ret

    def has_account_by_address(self, address):
        try:
            (index, account) = self.__wallet.find_account_by_address_hex(address)
            if account is None:
                ret = result(error.SUCCEED, "", True)
            else:
                ret = result(error.SUCCEED, "", False)
        except Exception as e:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.EXCEPT, str(e), e)
        return ret

    def has_account(self):
        try:
            self.__wallet.get_account_by_address_or_refid(0)
            ret = result(error.SUCCEED, "", True)
        except Exception as e:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.EXCEPT, str(e), e)
        except ValueError as e: #account count is 0, so not found account
            ret = result(error.SUCCEED, "", False)
        return ret



class violasclient:
    __node = None
    def __init__(self, traceback_limit, nodes):
        self.__traceback_limit = traceback_limit
        self.__client = None
        if nodes is not None:
            ret = self.conn_node(nodes)
            if ret.state != error.SUCCEED:
                raise Exception("connect violas node failed.")

    def __del__(self):
        self.disconn_node()

    def conn_node(self, nodes):
        try:
            logger.debug("conn_node")
            if nodes is None or len(nodes) == 0:
                return result(error.ARG_INVALID, repr(nodes), "")
            
            for node in nodes:
                try:
                    client = Client.new(node.get("ip", "127.0.0.1"), node.get("port", 4001), node.get("validator", None), node.get("faucet", None))
                    logger.debug("connect violas node : ip = {} port = {} validator={} faucet ={}".format( \
                            node.get("ip", "127.0.0.1"), node.get("port", 4001), node.get("validator", None), node.get("faucet", None)))
                except Exception as e:
                    logger.debug(traceback.format_exc(self.__traceback_limit))
                    logger.error(str(e))
                else:
                    self.__client = client
                    self.__node = node
                    return result(error.SUCCEED, "", "")

            #not connect any violas node
            ret = result(error.FAILED,  "connect violas node failed.", "")
        except:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.EXCEPT, str(e), e)
        return ret
    
    def disconn_node(self):
        try:
            if self.__node is not None:
                del self.__node
                self.__node = None

            if self.__client is not None:
                del self.__client 
                self.__client = None
            ret = result(error.SUCCEED) 
        except Exception as e:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(e.message)
            ret = result(error.EXCEPT, e.message, e)
        return ret
   
    def create_violas_coin(self, account, is_blocking = True):
        try:
            logger.debug("create_violas_coin(account={}, is_blocking={})".format(account, is_blocking))
            self.__client.violas_publish(account, is_blocking)
            ret = result(error.SUCCEED) 
        except Exception as e:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.EXCEPT, str(e), e)
        return ret

    def mint_platform_coin(self, address, amount, is_blocking = True):
        try:
            logger.debug("start mint_platform_coin(address={}, amount={}, is_blocking={})".format(address, amount, is_blocking))
            self.__client.mint_coins(address, amount, is_blocking)
            ret = result(error.SUCCEED) 
        except Exception as e:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.EXCEPT, str(e), e)
        return ret

    def bind_module(self, account, module_address, is_blocking=True):
        try:
            logger.debug("start bind_module(account={}, module_address={}, is_blocking={}".format(account.address.hex(), module_address, is_blocking))
            self.__client.violas_init(account, module_address, is_blocking)
            ret = result(error.SUCCEED) 
        except Exception as e:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.EXCEPT, str(e), e)
        return ret

    def mint_violas_coin(self, address, amount, module_account, is_blocking=True):
        try:
            logger.debug("start mint_violas_coin(address={}, amount={}, module_account=R{}, is_blocking={})".format(address, amount, module_account.address.hex(), is_blocking))
            self.__client.violas_mint_coin(address, amount, module_account, is_blocking)
            ret = result(error.SUCCEED) 
        except Exception as e:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.EXCEPT, str(e), e)
        return ret

    def send_coin(self, from_account, to_address, amount, module_address, data=None, is_blocking=True):
        try:
            logger.debug("start send_coins(from_account={}, to_address={}, amount={}, module_address={}, data={}, is_blocking={})".format(from_account.address.hex(), to_address, amount, module_address, data, is_blocking))
            self.__client.violas_transfer_coin(from_account, to_address, amount, module_address, data, is_blocking=is_blocking)
            ret = result(error.SUCCEED) 
        except Exception as e:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.EXCEPT, str(e), e)
        return ret

    def get_platform_balance(self, account_address):
        try:
            logger.debug("get_platform_balance(address={})".format(account_address))
            balance = self.__client.get_balance(account_address)
            ret = result(error.SUCCEED, "", balance)
        except Exception as e:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.EXCEPT, str(e), e)
        return ret

    def get_violas_balance(self, account_address, module_address):
        try:
            logger.debug("get_balance(address={}, module={})".format(account_address, module_address))
            balance = self.__client.violas_get_balance(account_address, module_address)
            ret = result(error.SUCCEED, "", balance)
        except Exception as e:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.EXCEPT, str(e), e)
        return ret

    def get_account_state(self, address):
        try:
            logger.debug("start get_account_state(address={})".format(address))
            state =  self.__client.get_account_state(address)
            ret = result(error.SUCCEED, "", state)
        except Exception as e:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.EXCEPT, str(e), e)
        return ret

    def get_address_sequence(self, address):
        try:
            logger.debug("start get_address_sequence(address={})".format(address))
            num = self.__client.get_sequence_number(address)
            ret = result(error.SUCCEED, "", num)
        except Exception as e:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.EXCEPT, str(e), e)
        return ret

    def get_latest_transaction_version(self):
        try:
            logger.debug("start get_latest_transaction_version")
            datas = self.__client.get_latest_transaction_version()
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.EXCEPT, str(e), e)
        return ret

    def account_has_violas_module(self, address, module):
        try:
            logger.debug("start account_has_violas_module(address={}, module={})".format(address, module))
            vres = self.__client.violas_get_info(address)
            if vres is not None and module in vres.keys():
                ret = result(error.SUCCEED, "", True)
            else:
                ret = result(error.SUCCEED, "", False)
        except Exception as e:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.EXCEPT, str(e), e)
        return ret


class violasserver:
    __node = None
    def __init__(self, traceback_limit, nodes):
        self.__traceback_limit = traceback_limit
        self.__server= None
        assert nodes is not None, "nodes is None"
        if nodes is not None:
            ret = self.conn_node(nodes)
            if ret.state != error.SUCCEED:
                raise Exception("connect violas servier failed.")

    def __del__(self):
        self.disconn_node()

    def conn_node(self, nodes):
        try:
            logger.debug("conn_server")
            if nodes is None or len(nodes) == 0:
                return result(error.ARG_INVALID, repr(nodes), "")
            
            for node in nodes:
                try:
                    server = ""
                    #server = Client.new(node["ip"], node["port"], node["user"], node["password"])
                    logger.debug("connect violas server: ip = {} port = {} user={} password={}".format( \
                            node["ip"], node["port"], node["user"], node["password"]))
                    self.__node = node
                except Exception as e:
                    logger.debug(traceback.format_exc(self.__traceback_limit))
                    logger.error(str(e))
                else:
                    self.__server = server 
                    self.__node = node
                    return result(error.SUCCEED, "", "")

            #not connect any violas node
            ret = result(error.FAILED,  "connect violas node failed.", "")
        except:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.EXCEPT, str(e), e)
        return ret
    
    def disconn_node(self):
        try:
            logger.debug("start disconn_node")
            if self.__node is not None:
                del self.__node
                self.__node = None

            if self.__server is not None:
                del self.__server
                self.__server = None
            ret = result(error.SUCCEED) 
        except Exception as e:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.EXCEPT, str(e), e)
        return ret
   
    def get_transactions(self, address, module, start):
        try:
            logger.debug("start get_transactions(address={}, module={}, start={})".format(address, module, start))
            datas = []
            #sequence = random.randint(1, 10000)
            #version = random.randint(1, 9999999)
            #datas = [{"address": "f086b6a2348ac502c708ac41d06fe824c91806cabcd5b2b5fa25ae1c50bed3c6", "amount":10000, "sequence":sequence,  "version":version, "baddress":"2N8qe3KogEF3DjWNsDGr2qLQGgQD3g9oTnc"}]
            url = "http://{}:{}/1.0/violas/vbtc/transaction?receiver_address={}&module_address={}&start_version={}"\
                    .format(self.__node["ip"], self.__node["port"], address, module, start)
            response = requests.get(url)

            ret = result(error.FAILED, "", "")
            if response is None:
                ret = result(error.FAILED, "", "")
            else:
                jret = response.json()
                code = jret["code"]
                message = jret["message"]
                if code != 2000:
                    return result(error.FAILED, message)
                
                for data in jret["data"]:
                    version     = int(data["version"])
                    address     = data["sender_address"]
                    amount      = int(data["amount"])
                    sequence    = int(data["sequence_number"])
                    baddress    = data["btc_address"]
                    datas.append({"address": address, "amount":amount, "sequence":sequence,  "version":version, "baddress":baddress})
                ret = result(error.SUCCEED, message, datas)
        except Exception as e:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.EXCEPT, str(e), e)
        return ret
    def has_transaction(self, address, module, baddress, sequence, amount, version, receiver):
        return result(error.SUCCEED, "", True)
        try:
            logger.debug("start has_transaction(address={}, module={}, baddress={}, sequence={}, amount={}, version={}, receiver={})"\
                    .format(address, module, baddress, sequence, amount, version, receiver))
            ret = result(error.FAILED, "", "")
            data = {
                    "version":version,
                    "sender_address":address,
                    "sequence_number":sequence,
                    "amount":amount,
                    "btc_address":baddress,
                    "module":module,
                    "receiver":receiver,
                    }
            url = "http://{}:{}/1.0/violas/vbtc/transaction".format(self.__node["ip"], self.__node["port"])
            headers = headers = {'Content-Type':'application/json'}
            response = requests.post(url,  data = data)

            if response is not None:
                jret = json.loads(response.text)
                if jret["code"] == 2000:
                    ret = result(error.SUCCEED, jret["message"], True)
                else:
                    ret = result(error.SUCCEED, jret["message"], False)
        except Exception as e:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.EXCEPT, str(e), e)
        return ret

