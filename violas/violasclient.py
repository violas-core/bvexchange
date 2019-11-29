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
#from .models import BtcRpc
from enum import Enum

#module name
name="violasclient"

#load logging
logger = log.logger.getLogger(name) 

#btc_url = "http://%s:%s@%s:%i"


class violaswallet:
    __traceback_limit       = 0
    __btc_url               = "http://%s:%s@%s:%i"
    __rpcuser               = "btc"
    __rpcpassword           = "btc"
    __rpcip                 = "127.0.0.1"
    __rpcport               = 9409
    __rpc_connection        = ""
    __wallet_name           = "vwallet"
    
    def __init__(self, traceback_limit, wallet_name = None):
        self.__traceback_limit = traceback_limit
        if wallet_name is not None:
            ret = self.load_wallet(wallet_name)
            if ret.state != error.SUCCEED:
                raise Exception("load wallet failed.")

    def __del__(self):
        logger.debug("start __del__")
        self.dump_wallet()

    def load_wallet(self, wallet_name):
        try:
            logger.debug("start load_wallet")
            self.__wallet_name = wallet_name
            if os.path.isfile(self.__wallet_name):
                self.__wallet = WalletLibrary.recover(self.__wallet_name)
                #self.__wallet.recover(self.__wallet_name)
                ret = result(error.SUCCEED, "", "")
            else:
                ret = result(error.ARG_INVALID, "not found wallet file", "")
                self.__wallet = WalletLibrary.new()

        except Exception as e:
            logger.error(traceback.format_exc(self.__traceback_limit))
            ret = result(error.EXCEPT, e, "")
        return ret

    def dump_wallet(self):
        try:
            logger.debug("start dump_wallet")
            self.__wallet.write_recovery(self.__wallet_name)
            ret = result(error.SUCCEED)
        except Exception as e:
            logger.error(traceback.format_exc(self.__traceback_limit))
            ret = result(error.EXCEPT, e, "")
        return ret

    def new_account(self):
        try:
            logger.debug("start new_wallet")
            account = self.__wallet.new_account();
            ret = result(error.SUCCEED, "", account)
        except Exception as e:
            logger.error(traceback.format_exc(self.__traceback_limit))
            ret = result(error.EXCEPT, e, "")
        return ret

    def get_account(self, addressorid):
        try:
            logger.debug("get_account")
            account = self.__wallet.get_account_by_address_or_refid(addressorid)
            ret = result(error.SUCCEED, "", account)
        except Exception as e:
            logger.error(traceback.format_exc(self.__traceback_limit))
            ret = result(error.EXCEPT, e, "")
        return ret

    def has_account_by_address(self, address):
        try:
            logger.debug("start has_account_by_address")
            (index, account) = self.__wallet.find_account_by_address_hex(address)
            if account is None:
                ret = result(error.SUCCEED, "", True)
            else:
                ret = result(error.SUCCEED, "", False)
        except Exception as e:
            logger.error(traceback.format_exc(self.__traceback_limit))
            ret = result(error.EXCEPT, e, "")
        return ret

    def has_account_by(self):
        try:
            logger.debug("start has_account_by_address")
            self.__wallet.get_account_by_address_or_refid(0)
            ret = result(error.SUCCEED, "", True)
        except Exception as e:
            logger.error(traceback.format_exc(self.__traceback_limit))
            ret = result(error.EXCEPT, e, "")
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
                except Exception as e:
                    logger.error(traceback.format_exc(self.__traceback_limit))
                else:
                    self.__client = client
                    self.__node = node
                    return result(error.SUCCEED, "", "")

            #not connect any violas node
            ret = result(error.FAILED,  "connect violas node failed.", "")
        except:
            logger.error(traceback.format_exc(self.__traceback_limit))
            ret = result(error.EXCEPT, e, "")
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
            logger.error(traceback.format_exc(self.__traceback_limit))
            ret = result(error.EXCEPT, e, "")
        return ret
    
    def send_vtoken(self, from_account, to, token, amount, is_blocking = True):
        try:
            logger.debug("send_vbtc")
            self.__client.violas_transfer_coin(from_account, to, amount, token, is_blocking) #blocking
            sequence = self.__client.get_sequence_number(from_account)
            ret = result(error.SUCCEED, "", sequence) 
        except Exception as e:
            logger.error(traceback.format_exc(self.__traceback_limit))
            ret = result(error.EXCEPT, e, "")
        return ret

    def create_violas_coin(self, account, is_blocking = True):
        try:
            logger.debug("create_violas_coin")
            self.__client.violas_publish(account, is_blocking)
            ret = result(error.SUCCEED) 
        except Exception as e:
            logger.error(traceback.format_exc(self.__traceback_limit))
            ret = result(error.EXCEPT, e, "")
        return ret

    def mint_platform_coin(self, address, amount, is_blocking = True):
        try:
            logger.debug("mint_platform_coin")
            self.__client.mint_coins(address, amount, is_blocking)
            ret = result(error.SUCCEED) 
        except Exception as e:
            logger.error(traceback.format_exc(self.__traceback_limit))
            ret = result(error.EXCEPT, e, "")
        return ret

    def bind_module(self, account, module_address, is_blocking=True):
        try:
            logger.debug("start bind_module")
            self.__client.violas_init(account, module_address, is_blocking)
            ret = result(error.SUCCEED) 
        except Exception as e:
            logger.error(traceback.format_exc(self.__traceback_limit))
            ret = result(error.EXCEPT, e, "")
        return ret

    def mint_violas_coin(self, address, amount, account, is_blocking=True):
        try:
            logger.debug("mint_violas_coin")
            self.__client.violas_mint_coin(address, amount, account, is_blocking)
            ret = result(error.SUCCEED) 
        except Exception as e:
            logger.error(traceback.format_exc(self.__traceback_limit))
            ret = result(error.EXCEPT, e, "")
        return ret

    def send_coins(self, from_account, to_address, amount, module_address, is_blocking=True):
        try:
            logger.debug("send_coins")
            self.__client.violas_transfer_coin(from_account, to_address, amount, module_address, is_blocking=is_blocking)
            ret = result(error.SUCCEED) 
        except Exception as e:
            logger.error(traceback.format_exc(self.__traceback_limit))
            ret = result(error.EXCEPT, e, "")
        return ret

    def get_balance(self, account_address, module_address):
        try:
            logger.debug("get_balance")
            balance = self.__client.violas_get_balance(account_address, module_address)
            ret = result(error.SUCCEED, "", balance)
        except Exception as e:
            logger.error(traceback.format_exc(self.__traceback_limit))
            ret = result(error.EXCEPT, e, "")
        return ret

    def get_account_state(self, address):
        return self.__client.get_account_state(address)

    def get_address_sequence(self, address):
        try:
            num = self.__client.get_sequence_number(address)
            ret = result(error.SUCCEED, "", num)
        except Exception as e:
            logger.error(traceback.format_exc(self.__traceback_limit))
            ret = result(error.EXCEPT, e, "")
        return ret



wallet_name = "vwallet"
exg = violasclient(setting.traceback_limit)
def test_client():
    logger.debug("start test_conn")
    global wallet_name
    client = violasclient(setting.traceback_limit)
    ret = client.conn_node(setting.violas_nodes)
    if(ret.state != error.SUCCEED):
        return
    wallet = violaswallet(setting.traceback_limit)
    ret = wallet.load_wallet(wallet_name)

    vbtc = wallet.new_account().datas
    account = wallet.new_account().datas

    #mint platform coin to address
    client.mint_platform_coin(vbtc.address, 100)
    client.mint_platform_coin(account.address, 100)

    #create vbtc 
    client.create_violas_coin(vbtc)

    #bind to vbtc
    client.bind_module(vbtc, vbtc.address)
    client.bind_module(account, vbtc.address)

    #generate vbtc
    client.mint_violas_coin(vbtc.address, 100, vbtc)

    client.send_coins(vbtc, account.address, 10, vbtc.address)

    ret = client.get_balance(vbtc.address, vbtc.address)
    logger.debug("balance: {0}".format(ret.datas)) 

    logger.debug("account.address({0}): {1}".format(type(account.address), account.address.decode()))
    json_print(client.get_account_state(account.address).to_json())

def test_wallet():
    global wallet_name
    target_address_hex = "cd0476e85ecc5fa71b61d84b9cf2f7fd524689a4f870c46d6a5d901b5ac1fdb2"
    wallet = violaswallet(setting.traceback_limit, wallet_name)
    #ac1 = wallet.new_account()
    #ac2 = wallet.new_account()

    i = 0
    while i < 4:
        logger.debug("i = {}".format(i))
        ret = wallet.get_account(str(i))
        if ret.state != error.SUCCEED:
           break 
        account = ret.datas
        logger.debug("account.address({0}): {1}".format(account.address, account.address.hex()))
        i += 1

    ret = wallet.get_account(target_address_hex)
    if ret.state == error.SUCCEED:
        logger.debug("found address:{}".format(target_address_hex))
    else:
        logger.debug("not found address:{}".format(target_address_hex))


def test_libra():
    print(sys.path)
    wallet = WalletLibrary.new()
    a1 = wallet.new_account()
    a2 = wallet.new_account()
    client = Client.new('18.220.66.235',40001, "consensus_peers.config.toml", "temp_faucet_keys")
    client.mint_coins(a1.address, 100, True)
    client.mint_coins(a2.address, 100, True)

    client.violas_publish(a1, True)
    client.violas_init(a1, a1.address, True)
    client.violas_init(a2, a1.address, True)
    client.violas_mint_coin(a1.address, 100, a1, True)
    print("before............")
    print("libra balance:", "a1=", client.get_balance(a1.address), "a2=", client.get_balance(a2.address))
    print("violas balance:", "a1=", client.violas_get_balance(a1.address, a1.address), "a2=", client.violas_get_balance(a2.address, a1.address))

    print("before:", client.violas_get_balance(a1.address, a1.address), client.violas_get_balance(a2.address, a1.address))
    client.violas_transfer_coin(a1, a2.address, 20, a1.address, is_blocking=True)
    print("after:", client.violas_get_balance(a1.address, a1.address), client.violas_get_balance(a2.address, a1.address))

def main():
       logger.debug("start main")
       test_libra()
       #test_client()
       #test_wallet()

if __name__ == "__main__":
    main()
