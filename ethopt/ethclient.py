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
from ethopt.ethproxy import ethproxy as clientproxy
from enum import Enum
from baseobject import baseobject
from comm.functions import split_full_address
import redis

import web3
from web3 import Web3

#module name
name="eclient"

class ethwallet(baseobject):
    
    def __init__(self, name, wallet_name, chain="violas"):
        assert wallet_name is not None, "wallet_name is None"
        baseobject.__init__(self, name)
        self.__wallet = None
        if wallet_name is not None:
            ret = self.__load_wallet(wallet_name, chain)
            if ret.state != error.SUCCEED:
                raise Exception(f"load wallet[{wallet_name}] failed.")

    def __del__(self):
        pass

    def __load_wallet(self, wallet_name, chain="violas"):
        try:
            self.__wallet_name = wallet_name

            if chain in ("violas"):
                from vlsopt.violasproxy import walletproxy
            elif chain in ("libra"):
                from vlsopt.libraproxy import walletproxy
            else:
                raise Exception(f"chain name[{chain}] unkown. can't connect libra/violas wallet")

            if os.path.isfile(self.__wallet_name):
                self.__wallet = walletproxy.load(self.__wallet_name)
                ret = result(error.SUCCEED, "", "")
            else:
                ret = result(error.SUCCEED, "not found wallet file", "")
                raise Exception(f"not found {self.name()} wallet file({self.__wallet_name})")
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

    def get_account(self, addressorid):
        try:
            address = addressorid
            if isinstance(addressorid, str) and len(addressorid) >= min(VIOLAS_ADDRESS_LEN):
                auth, addr = self.split_full_address(addressorid).datas
                address = addr

            account = self.__wallet.get_account_by_address_or_refid(address)
            if account is None:
                ret = result(error.ARG_INVALID)
            else:
                ret = result(error.SUCCEED, "", account)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def find_account_by_address_hex(self, address):
        (auth, addr) = self.split_full_address(address).datas
        for i in range(len(self.__wallet.accounts)):
            if self.__wallet.accounts[i].address.hex == addr:
                return (i, self.__wallet.accounts[i])

        return (-1, None)

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
            (auth, addr) = split_full_address(address, auth_key_prefix)
            ret = result(error.SUCCEED, datas = (auth, addr))
        except Exception as e:
            ret = parse_except(e)
        return ret

class ethclient(baseobject):
    def __init__(self, name, nodes, chain = "ethereum"):
        baseobject.__init__(self, name, chain)
        self.__client = None
        self.__node = None
        if nodes is not None:
            ret = self.conn_node(name, nodes, chain)
            if ret.state != error.SUCCEED:
                raise Exception(f"connect {chain} node failed.")

    def __del__(self):
        self.disconn_node()

    def clientname(self):
        return self.__client.clientname()

    def load_contract(self, name, address):
        self.__client.load_contract(name, address)

    def conn_node(self, name, nodes, chain = "ethereum"):
        try:
            if nodes is None or len(nodes) == 0:
                return result(error.ARG_INVALID, repr(nodes), "")
            

            for node in nodes:
                try:
                    if self.work() == False:
                        return result(error.FAILED, f"connect {chain} work stop")

                    self._logger.debug("try connect node({}) : host = {} port = {} validator={} faucet ={}".format( \
                            node.get("name", ""), node.get("host"), node.get("port"), node.get("validator"), node.get("faucet")))
                    client = clientproxy(host=node.get("host"), \
                            port=node.get("port"), \
                            timeout = node.get("timeout"), \
                            debug = node.get("debug", False))
                    if not client.is_connected():
                        self._logger.info(f"connect {chain} node failed({e}). test next...")
                        continue

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


    def send_coin(self, from_account, to_address, amount, token_id, module_address = None, data=None, auth_key_prefix = None, is_blocking=True, max_gas_amount = 100_0000):
        try:
            if (len(to_address) not in VIOLAS_ADDRESS_LEN) or (amount < 1) or ((module_address is not None) and (len(module_address) not in VIOLAS_ADDRESS_LEN)):
                return result(error.ARG_INVALID)

            self.__client.send_coin(sender_account=from_account, receiver_address=addr, \
                    micro_coins=amount, token_id = token_id, module_address=module_addr, data=data, auth_key_prefix = auth_key_prefix, is_blocking=is_blocking, max_gas_amount = max_gas_amount)
            ret = result(error.SUCCEED) 
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_balance(self, account_address, token_id = None, module_address = None):
        try:
            balance = self.__client.get_balance(account_address = addr, currency_code = token_id)
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
            ret = result(error.SUCCEED, "", num - 1)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_transaction_version(self, address, sequence):
        try:
            num = self.__client.get_account_transaction(address, sequence)
            ret = result(error.SUCCEED, "", num)
        except Exception as e:
            ret = parse_except(e)
        return ret
    def get_address_version(self, address):
        try:
            ret = self.get_address_sequence(address)
            if ret.state != error.SUCCEED:
                return ret

            ret = self.get_transaction_version(address, ret.datas)
            if ret.state != error.SUCCEED:
                return ret

            ret = result(error.SUCCEED, "", ret.datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_latest_transaction_version(self):
        try:
            datas = self.__client.get_latest_version()
            ret = result(error.SUCCEED, "", datas)
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

def main():
    pass
if __name__ == "__main__":
    main()