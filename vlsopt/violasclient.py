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
from db.dbb2v import dbb2v
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from enum import Enum
from baseobject import baseobject
from comm.functions import split_full_address
import redis

VIOLAS_ADDRESS_LEN = comm.values.VIOLAS_ADDRESS_LEN

#module name
name="vclient"

class violaswallet(baseobject):
    
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
            self._logger.debug("start load_wallet({})".format(wallet_name))
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
                self.__wallet = walletproxy.new()
                self._logger.warning(f"new wallet created.walletname:{self.__wallet_name}")

        except Exception as e:
            ret = parse_except(e)
        return ret

    def dump_wallet(self):
        try:
            if self.__wallet is not None:
                self.__wallet.write_recovery(self.__wallet_name)
                self.__wallet = None
                pass
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def new_account(self):
        try:
            self._logger.info("start new_account")
            account = self.__wallet.new_account();
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
                print(f"auth_key_prefix: {auth} ,address: {addr}")

            account = self.__wallet.get_account_by_address_or_refid(address)
            if account is None:
                ret = result(error.ARG_INVALID)
            else:
                ret = result(error.SUCCEED, "", account)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def has_account_by_address(self, address):
        try:
            (auth_key_prefix, addr) = self.split_full_address(address).datas
            (index, account) = self.__wallet.find_account_by_address_hex(addr)
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

class violasclient(baseobject):
    __node = None
    def __init__(self, name, nodes, chain = "violas"):
        baseobject.__init__(self, name, chain)
        self.__client = None
        if nodes is not None:
            ret = self.conn_node(name, nodes, chain)
            if ret.state != error.SUCCEED:
                raise Exception(f"connect {chain} node failed.")

    def __del__(self):
        self.disconn_node()

    def conn_node(self, name, nodes, chain = "violas"):
        try:
            if nodes is None or len(nodes) == 0:
                return result(error.ARG_INVALID, repr(nodes), "")
            
            if chain in ("violas"):
                from vlsopt.violasproxy import clientproxy
            elif chain in ("libra"):
                from vlsopt.libraproxy import clientproxy
            else:
                raise Exception(f"chain name[{chain}] unkown. can't connect libra/violas node")

            for node in nodes:
                try:
                    if self.work() == False:
                        return result(error.FAILED, f"connect {chain} work stop")

                    self._logger.debug("try connect node({}) : host = {} port = {} validator={} faucet ={}".format( \
                            node.get("name", ""), node.get("host"), node.get("port"), node.get("validator"), node.get("faucet")))
                    client = clientproxy.connect(host=node.get("host"), \
                            port=node.get("port"), \
                            faucet_file = node.get("faucet"), \
                            timeout = node.get("timeout"), \
                            debug = node.get("debug", False))
                    client.get_latest_version()
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
            if self.__node is not None:
                del self.__node
                self.__node = None

            if self.__client is not None:
                del self.__client 
                self.__client = None
            ret = result(error.SUCCEED) 
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_token_list(self, address = None):
        try:
            token_list = self.__client.get_registered_currencies()
            if address is not None:
                ret = self.get_account_state(address)
                if ret.state != error.SUCCEED:
                    return ret
                token_list = [token_id for token_id in token_list if ret.datas.is_published(token_id)]
            ret = result(error.SUCCEED, datas = token_list)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def bind_token_id(self, account, token_id):
        try:
            datas = self.__client.add_currency_to_account(account, token_id)
            ret = result(error.SUCCEED, datas = datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def has_token_id(self, address, token_id):
        try:
            state = False
            ret = self.get_account_state(address)
            if ret.state != error.SUCCEED:
                return ret
            ret = result(error.SUCCEED, datas = ret.datas.is_published(token_id))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def split_full_address(self, address, auth_key_prefix = None):
        try:
            datas = split_full_address(address, auth_key_prefix)
            ret = result(error.SUCCEED, datas = datas)
            self._logger.debug(f"split full address: address ={datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def mint_coin(self, address, amount, token_id, module = None, auth_key_prefix = None, is_blocking=True):
        try:
            self._logger.info(f"start mint_coin(address={address}, amount={amount}, token_id={token_id}, module={module}, auth_key_prefix={auth_key_prefix}, is_blocking={is_blocking})")
            (auth, addr) = self.split_full_address(address, auth_key_prefix).datas
            (_, mod) = self.split_full_address(module).datas

            self.__client.mint_coin(receiver_address = addr, micro_coins = amount, currency_code = token_id, currency_module_address = mod, auth_key_prefix = auth, is_blocking=is_blocking)
            ret = result(error.SUCCEED) 
        except Exception as e:
            ret = parse_except(e)
        return ret

    def send_violas_coin(self, from_account, to_address, amount, token_id, module_address = None, data=None, auth_key_prefix = None, is_blocking=True, max_gas_amount = 100_0000):
        return self.send_coin(from_account, to_address, amount, token_id, module_address, data, auth_key_prefix, is_blocking, max_gas_amount)

    def send_coin(self, from_account, to_address, amount, token_id, module_address = None, data=None, auth_key_prefix = None, is_blocking=True, max_gas_amount = 100_0000):
        try:
            self._logger.info(f"start send_coin(from_account={from_account.address.hex()}, to_address={to_address}, amount={amount}, token_id = {token_id}, module_address={module_address}, data={data}, auth_key_prefix={auth_key_prefix}, is_blocking={is_blocking})")

            if (len(to_address) not in VIOLAS_ADDRESS_LEN) or (amount < 1) or ((module_address is not None) and (len(module_address) not in VIOLAS_ADDRESS_LEN)):
                return result(error.ARG_INVALID)

            (_, mod) = self.split_full_address(module_address).datas
            if mod in ("0000000000000000000000000000000000000000000000000000000000000000", "00000000000000000000000000000000"):
                module_address = None

            (auth, addr) = self.split_full_address(to_address, auth_key_prefix).datas
            (_, module_addr) = self.split_full_address(module_address).datas

            self.__client.send_coin(sender_account=from_account, receiver_address=addr, \
                    micro_coins=amount, token_id = token_id, module_address=module_addr, data=data, auth_key_prefix = auth_key_prefix, is_blocking=is_blocking, max_gas_amount = max_gas_amount)
            ret = result(error.SUCCEED) 
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_balance(self, account_address, module_address = None, token_id = None):
        return self.get_violas_balance(account_address, module_address, token_id)

    def get_violas_balance(self, account_address, module_address = None, token_id = None):
        try:
            self._logger.debug(f"get_balance(address={account_address}, module={module_address}, token_id={token_id})")
            (_, addr) = self.split_full_address(account_address).datas
            (_, module_addr) = self.split_full_address(module_address).datas

            balance = self.__client.get_balance(account_address = addr, currency_code = token_id, currency_module_address = module_addr)
            ret = result(error.SUCCEED, "", balance)
            self._logger.debug(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_balances(self, account_address):
        try:
            self._logger.debug(f"get_balances(address={account_address}")
            (_, addr) = self.split_full_address(account_address).datas

            balance = self.__client.get_balances(account_address = addr)
            ret = result(error.SUCCEED, "", balance)
            self._logger.debug(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_account_state(self, address, module = None):
        try:
            self._logger.debug(f"start get_account_state(address={address}, modlue = {module})")
            (_, addr) = self.split_full_address(address).datas
            (_, mod) = self.split_full_address(module).datas
            state =  self.__client.get_account_state(addr)
            ret = result(error.SUCCEED, "", state)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_address_sequence(self, address):
        try:
            self._logger.debug("start get_address_sequence(address={})".format(address))
            (_, addr) = self.split_full_address(address).datas
            num = self.__client.get_sequence_number(addr)
            ret = result(error.SUCCEED, "", num - 1)
            self._logger.debug(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_transaction_version(self, address, sequence):
        try:
            self._logger.debug(f"start get_transaction_version(address={address}, sequence={sequence})")
            (_, addr) = self.split_full_address(address).datas
            num = self.__client.get_account_transaction(addr, sequence).get_version()
            ret = result(error.SUCCEED, "", num)
            self._logger.debug(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret
    def get_address_version(self, address):
        try:
            self._logger.debug(f"start get_address_version(address={address})")
            (_, addr) = self.split_full_address(address).datas
            ret = self.get_address_sequence(addr)
            if ret.state != error.SUCCEED:
                return ret

            ret = self.get_transaction_version(address, ret.datas)
            if ret.state != error.SUCCEED:
                return ret

            ret = result(error.SUCCEED, "", ret.datas)
            self._logger.debug(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_latest_transaction_version(self):
        try:
            self._logger.debug("start get_latest_transaction_version")
            datas = self.__client.get_latest_version()
            ret = result(error.SUCCEED, "", datas)
            self._logger.debug(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_transactions(self, start_version, limit = 1, fetch_event=True):
        try:
            self._logger.debug(f"start get_transactions(start_version={start_version}, limit={limit}, fetch_event={fetch_event})")
            datas = self.__client.get_transactions(start_version, limit, fetch_event)
            ret = result(error.SUCCEED, "", datas)
            self._logger.debug(f"result: {len(ret.datas)}")
        except Exception as e:
            ret = parse_except(e)
        return ret

class violasserver(baseobject):
    __node = None
    def __init__(self, name, nodes):
        baseobject.__init__(self, name)
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
            self._logger.debug("conn_server")
            if nodes is None or len(nodes) == 0:
                return result(error.ARG_INVALID, repr(nodes), "")
            
            for node in nodes:
                try:
                    server = ""
                    #server = Client.new(node["host"], node["port"], node["user"], node["password"])
                    self._logger.debug("connect violas server: host= {} port = {} user={} password={}".format( \
                            node["host"], node["port"], node["user"], node["password"]))
                    self.__node = node
                except Exception as e:
                    parse_except(e)
                else:
                    self.__server = server 
                    self.__node = node
                    return result(error.SUCCEED, "", "")

            #not connect any violas node
            ret = result(error.FAILED,  "connect violas node failed.", "")
        except:
            ret = parse_except(e)
        return ret
    
    def disconn_node(self):
        try:
            self._logger.debug("start disconn_node")
            if self.__node is not None:
                del self.__node
                self.__node = None

            if self.__server is not None:
                del self.__server
                self.__server = None
            ret = result(error.SUCCEED) 
        except Exception as e:
            ret = parse_except(e)
        return ret
   
    def get_transactions(self, address, module, start):
        try:
            self._logger.debug("start get_transactions(address={}, module={}, start={})".format(address, module, start))
            datas = []
            url = "http://{}:{}/1.0/violas/vbtc/transaction?receiver_address={}&module_address={}&start_version={}"\
                    .format(self.__node["host"], self.__node["port"], address, module, start)
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
                    baddress    = data["to_address"]
                    datas.append({"address": address, "amount":amount, "sequence":sequence,  "version":version, "baddress":baddress})
                ret = result(error.SUCCEED, message, datas)
        except Exception as e:
            ret = parse_except(e)
        finally:
            self._logger.debug("end get_transactions.")
        return ret

    def has_transaction(self, address, module, baddress, sequence, amount, version, receiver):
        try:
            self._logger.debug("start has_transaction(address={}, module={}, baddress={}, sequence={}, amount={}, version={}, receiver={})"\
                    .format(address, module, baddress, sequence, amount, version, receiver))
            ret = result(error.FAILED, "", "")
            data = {
                    "version":version,
                    "sender_address":address,
                    "sequence_number":sequence,
                    "amount":amount,
                    "to_address":baddress,
                    "module":module,
                    "receiver":receiver,
                    }
            url = "http://{}:{}/1.0/violas/vbtc/transaction".format(self.__node["host"], self.__node["port"])
            headers = headers = {'Content-Type':'application/json'}
            response = requests.post(url,  json = data)
            if response is not None:
                jret = json.loads(response.text)
                if jret["code"] == 2000:
                    ret = result(error.SUCCEED, jret["message"], True)
                else:
                    ret = result(error.SUCCEED, jret["message"], False)
        except Exception as e:
            ret = parse_except(e)
        finally:
            self._logger.debug("end has_transaction.")
        return ret


def main():
    pass
if __name__ == "__main__":
    main()
