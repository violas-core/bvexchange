#!/usr/bin/python3
import operator
import sys
import json
import os
sys.path.append(os.getcwd())
sys.path.append("{}".format(os.getcwd()))
sys.path.append("..")
import log
import log.logger
import traceback
import datetime
import sqlalchemy
import stmanage
import requests
import random
import comm
import comm.error
import comm.result
import comm.values
from comm import version
from comm.result import result, parse_except
from comm.error import error
from comm.functions import (
        is_mnemonic,
        output_args
        )
from ethopt.ethproxy import (
        ethproxy as clientproxy,
        walletproxy,
        VLSMPROOF_MAIN_NAME,
        VLSMPROOF_DATAS_NAME,
        VLSMPROOF_STATE_NAME
        )
from enum import Enum
from baseobject import baseobject
import redis

import web3
from web3 import Web3
from ethopt.ethproxy import (
        VLSMPROOF_MAIN_NAME,
        contract_codes,
        )

from comm.values import (
        ETH_ADDRESS_LEN
        )
#module name
name="eclient"


VLSMPROOF_MAIN_ADDRESS = contract_codes[VLSMPROOF_MAIN_NAME]["address"]
ETH_ADDRESS_LEN = comm.values.ETH_ADDRESS_LEN
class ethwallet(baseobject):
    
    def __init__(self, name, wallet, chain="ethereum", main_address = None):
        assert wallet is not None, "wallet is None"
        baseobject.__init__(self, name)
        self.__wallet = None
        self.set_vlsmproof_main_address(main_address)

        if wallet is not None:
            ret = self.__load_wallet(wallet, chain)
            if ret.state != error.SUCCEED:
                raise Exception(f"load wallet[{wallet}] failed.")

    def __del__(self):
        pass

    def set_vlsmproof_main_address(self, main_address):
        if main_address:
            VLSMPROOF_MAIN_ADDRESS = main_address

    def __load_wallet(self, wallet, chain="ethereum"):
        try:
            self.__wallet_name = wallet

            if os.path.isfile(wallet):
                self.__wallet = walletproxy.load(wallet)
                ret = result(error.SUCCEED, "", "")
            elif is_mnemonic(wallet):
                self.__wallet_name = None
                self.__wallet = walletproxy.loads(wallet)
                ret = result(error.SUCCEED, "", "")
            else:
                ret = result(error.SUCCEED, "not found wallet file", "")
                raise Exception(f"not found {self.name()} wallet file({wallet})")
                self.__wallet = walletproxy.new()

        except Exception as e:
            ret = parse_except(e)
        return ret

    def save(self):
        try:
            if self.__wallet is not None and self.__wallet_name:
                self.__wallet.write_recovery(self.__wallet_name)
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def dump_wallet(self):
        try:
            if self.__wallet is not None:
                self.save()
                self.__wallet = None
                pass
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    @classmethod
    def is_valid_address(self, address):
        try:
            ret = result(error.SUCCEED, datas = walletproxy.is_valid_address(address))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def new_account(self):
        try:
            account = self.__wallet.new_account();
            self.save()
            ret = result(error.SUCCEED, "", account)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_account_count(self):
        return len(self.__wallet.accounts)

    def is_main_contract_address(self, address):
        return address == VLSMPROOF_MAIN_ADDRESS

    def get_account(self, addressorid):
        try:
            if isinstance(addressorid, str) and addressorid == VLSMPROOF_MAIN_ADDRESS:
                return result(error.SUCCEED, "", VLSMPROOF_MAIN_ADDRESS)

            account = self.__wallet.get_account_by_address_or_refid(addressorid)
            if account is None:
                ret = result(error.ARG_INVALID)
            else:
                ret = result(error.SUCCEED, "", account)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def find_account_by_address_hex(self, address):
        return self.__wallet.find_account_by_address_hex(address)

    def has_account_by_address(self, address):
        try:
            _, account = self.find_account_by_address_hex(address)
            if account is None:
                ret = result(error.SUCCEED, "", False)
            else:
                ret = result(error.SUCCEED, "", True)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def has_account(self):
        try:
            self.__wallet.get_account_by_address_or_refid(0)
            ret = result(error.SUCCEED, "", True)
        except ValueError as e: #account count is 0, so not found account
            ret = result(error.SUCCEED, "", False)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def split_full_address(self, address, auth_key_prefix = None):
        try:
            ret = result(error.SUCCEED, datas = (None, address))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def __getattr__(self, name):
        if name.startswith('__') and name.endswith('__'):
            # Python internal stuff
            raise AttributeError

class ethclient(baseobject):
    def __init__(self, name, nodes, chain = "ethereum", usd_chain = True):
        baseobject.__init__(self, name, chain)
        self.__client = None
        self.__node = None
        if nodes is not None:
            ret = self.conn_node(name, nodes, chain, usd_chain = usd_chain)
            if ret.state != error.SUCCEED:
                raise Exception(f"connect {chain} node failed.")

    def __del__(self):
        self.disconn_node()

    def clientname(self):
        return self.__client.clientname()

    def load_vlsmproof(self, address):
        self.__client.load_vlsmproof(address)

    def load_contract(self, name):
        self.__client.load_contract(name)

    def set_contract_map_account(self, account):
        self._sender_map_account = account

    def map_account(self, account):
        if isinstance(account, str) and account == VLSMPROOF_MAIN_ADDRESS:
            return self._sender_map_account
        return account

    def conn_node(self, name, nodes, chain = "ethereum", usd_chain = False):
        try:
            if nodes is None or len(nodes) == 0:
                return result(error.ARG_INVALID, repr(nodes), "")
            

            for node in nodes:
                try:
                    if self.work() == False:
                        return result(error.FAILED, f"connect {chain} work stop")

                    self._logger.debug("try connect node({}) : host = {} port = {} chain_id = {}".format( \
                            node.get("name", ""), node.get("host"), node.get("port"), node.get("chain_id", 42)))
                    client = clientproxy(host=node.get("host"), \
                            port=node.get("port"), \
                            usd_chain = usd_chain
                            )
                    #if not client.is_connected():
                    #    self._logger.info(f"connect {chain} node failed({e}). test next...")
                    #    continue

                    self._logger.debug(f"connect {chain} node succeed.") 
                except Exception as e:
                    parse_except(e)
                    self._logger.info(f"connect {chain} node failed({e}). test next...")
                else:
                    self.__client = client
                    self.__node = node
                    return result(error.SUCCEED, "", "")

            #not connect any violas node
            ret = result(error.FAILED,  f"connect {chain} node failed.", "")
        except Exception as e:
            ret = parse_except(e)
        return ret
    
    def stop(self):
        self.work_stop()

    def disconn_node(self):
        try:
            ret = result(error.SUCCEED) 
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_syncing_state(self): 
        try:
            ret = result(error.SUCCEED, datas = self.__client.syncing_state()) 
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_balance(self, account_address, token_id, module_address = None):
        try:
            balance = self.__client.get_balance(account_address, token_id)
            ret = result(error.SUCCEED, "", balance)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_balances(self, account_address):
        try:
            balance = self.__client.get_balances(account_address)
            ret = result(error.SUCCEED, "", balance)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_address_sequence(self, address):
        try:
            num = self.__client.get_sequence_number(address)
            ret = result(error.SUCCEED, "", num)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_transaction_version(self, address, sequence):
        try:
            num = self.__client.get_account_transaction_version(address, sequence)
            ret = result(error.SUCCEED, "", num)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_address_version(self, address, sequence):
        try:
            ret = self.get_transaction_version(address, sequence)
            if ret.state != error.SUCCEED:
                return ret

            ret = result(error.SUCCEED, "", ret.datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_address_latest_version(self, address):
        try:
            ver = self.__client.get_account_latest_version(address)
            ret = result(error.SUCCEED, "", ver)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_latest_transaction_version(self):
        try:
            datas = self.__client.get_latest_version()
            ret = result(error.SUCCEED, "", datas - 1)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_transactions(self, start_version, limit = 1, fetch_event=True):
        try:
            datas = self.__client.get_transactions(start_version, limit, fetch_event)
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_transaction(self, version, fetch_event=True):
        try:
            datas = self.__client.get_transactions(version, 1 , fetch_event)
            ret = result(error.SUCCEED, "", datas[0] if datas is not None else None)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_rawtransaction(self, txhash):
        try:
            datas = self.__client.get_rawtransaction(txhash)
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_transaction(self, version, fetch_event=True):
        try:
            datas = self.__client.get_transactions(version, 1 , fetch_event)
            ret = result(error.SUCCEED, "", datas[0] if datas is not None else None)
        except Exception as e:
            ret = parse_except(e)
        return ret

    #the same to btc/violas get_decimals
    def get_decimals(self, token_id):
        return self.__client.get_decimals(token_id)

    def create_data_for_end(self, flag, opttype, tranid, *args, **kwargs):
        return {"type": "end", "flag": flag, "opttype":opttype,  \
                "version":kwargs.get("version", -1), "out_amount_real": kwargs.get("out_amount_real", 0)}

    def create_data_for_stop(self, flag, opttype, tranid, *args, **kwargs):
        return {"type": "stop", "flag": flag, "opttype":opttype, \
                "version":kwargs.get("version", -1)}

    def create_data_for_mark(self, flag, dtype, id, version, *args, **kwargs):
        return {"type": "mark", "flag": flag, "version":version }

    @output_args
    def approve(self, account, to_address, amount, token_id, **kwargs):
        try:
            datas = self.__client.approve(account, to_address, amount, token_id, **kwargs)
            ret = result(error.SUCCEED, datas = datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    @output_args
    def allowance(self, from_address, to_address, token_id, **kwargs):
        try:
            datas = self.__client.allowance(from_address, to_address, token_id, **kwargs)
            ret = result(error.SUCCEED, datas = datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    @output_args
    def send_proof(self, account, token_id, datas, **kwargs):
        try:
            datas = self.__client.send_proof(account, token_id, datas, **kwargs)
            ret = result(error.SUCCEED, datas = datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def send_coin_erc20(self, account, toaddress, amount, token_id, *args, **kwargs):
        return self.send_coin(account, toaddress, amount, token_id, data= {"type":"mark", "version": None},*args, **kwargs)

    def send_coin(self, account, toaddress, amount, token_id, data, *args, **kwargs):
        '''change state 
        '''
        try:
            sender_account = self.map_account(account)
            if data["type"] in ("end", "stop"):
                datas = self.__client.update_proof_state(sender_account, data["version"], data["type"])
            elif data["type"] == "mark":
                datas = self.__client.send_token(sender_account, toaddress, amount, token_id)
            else:
                raise Exception(f"type{type} is invald.")
            ret = result(error.SUCCEED if len(datas) > 0 else error.FAILED, "", datas = datas)
            self._logger.debug(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_token_list(self):
        try:
            ret = result(error.SUCCEED, datas = self.__client.token_name_list())
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_proof_contract_address(self, name):
        try:
            datas = None
            if name == "main":
                datas = self.__client.token_address(VLSMPROOF_MAIN_NAME)
            elif name == "datas":
                datas = self.__client.token_address(VLSMPROOF_DATAS_NAME)
            elif name == "state":
                datas = self.__client.token_address(VLSMPROOF_STATE_NAME)
            else:
                raise ValueError(f"name({name}) is invalid.")

            ret = result(error.SUCCEED, datas = datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_chain_id(self):
        try:
            ret = result(error.SUCCEED, datas = self.__client.get_chain_id())
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_token_min_amount(self, token_id):
        try:
            ret = result(error.SUCCEED, datas = self.__client.get_token_min_amount(token_id))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_token_max_amount(self, token_id):
        try:
            ret = result(error.SUCCEED, datas = self.__client.get_token_max_amount(token_id))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def __getattr__(self, name):
        if name.startswith('__') and name.endswith('__'):
            # Python internal stuff
            raise AttributeError
        return self.__client

def main():
    pass
if __name__ == "__main__":
    main()
