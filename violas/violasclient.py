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
    
    def __init__(self, traceback_limit, wallet_name = None):
        self.__traceback_limit = traceback_limit
        if wallet_name is not None:
            ret = self.load_wallet(wallet_name)
            if ret.state != error.SUCCEED:
                raise Exception("load wallet failed.")

    def __del__(self):
        self.dump_wallet()

    def load_wallet(self, wallet_name):
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
            logger.debug("get_account(addressorid = {})".format(addressorid))
            account = self.__wallet.get_account_by_address_or_refid(addressorid)
            ret = result(error.SUCCEED, "", account)
        except Exception as e:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.EXCEPT, str(e), e)
        return ret

    def has_account_by_address(self, address):
        try:
            logger.debug("start has_account_by_address(address = {})".format(address))
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

    def has_account_by(self):
        try:
            logger.debug("start has_account_by_address")
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
    def __init__(self, traceback_limit, nodes = None):
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
                    client = Client.new(node["ip"], node["port"], node["validator"], node["faucet"])
                    logger.debug("connect violas node : ip = {} port = {} validator={} faucet ={}".format( \
                            node["ip"], node["port"], node["validator"], node["faucet"]))
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
            state =  self.__client.get_account_state(address)
            ret = result(error.SUCCEED, "", state)
        except Exception as e:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.EXCEPT, str(e), e)
        return ret

    def get_address_sequence(self, address):
        try:
            num = self.__client.get_sequence_number(address)
            ret = result(error.SUCCEED, "", num)
        except Exception as e:
            logger.debug(traceback.format_exc(self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.EXCEPT, str(e), e)
        return ret


