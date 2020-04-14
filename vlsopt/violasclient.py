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
from comm import version
from comm.result import result, parse_except
from comm.error import error
from db.dbb2v import dbb2v
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from enum import Enum
from baseobject import baseobject
import redis

if version.cmp(1, 1, 1) >= 0:
    sys.path.append("../libviolas")
    sys.path.append("{}/libviolas".format(os.getcwd()))
    #from violas.client import Client
    from violas.wallet import Wallet
elif version.cmp(1, 1, 0) <= 0:
    sys.path.append("../liblibra")
    sys.path.append("{}/liblibra".format(os.getcwd()))
    from violas.wallet import Wallet

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
                sys.path.append("../libviolas")
                sys.path.append("{}/libviolas".format(os.getcwd()))
                from violas.wallet import Wallet
            elif chain in ("libra"):
                sys.path.append("../liblibra")
                sys.path.append("{}/liblibra".format(os.getcwd()))
                from violas.wallet import Wallet
            else:
                raise Exception(f"chain name[{chain}] unkown. can't connect libra/violas wallet")

            if os.path.isfile(self.__wallet_name):
                self.__wallet = Wallet.recover(self.__wallet_name)
                ret = result(error.SUCCEED, "", "")
            else:
                ret = result(error.SUCCEED, "not found wallet file", "")
                self.__wallet = Wallet.new()
                self._logger.warning("new wallet created")

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
        return self.__wallet.child_count

    def get_account(self, addressorid):
        try:
            account = self.__wallet.get_account_by_address_or_refid(addressorid)
            ret = result(error.SUCCEED, "", account)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def has_account_by_address(self, address):
        try:
            (index, account) = self.__wallet.find_account_by_address_hex(address)
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
                sys.path.append("../libviolas")
                sys.path.append("{}/libviolas".format(os.getcwd()))
                from violas.client import Client
            elif chain in ("libra"):
                sys.path.append("../liblibra")
                sys.path.append("{}/liblibra".format(os.getcwd()))
                from violas.client import Client
            else:
                raise Exception(f"chain name[{chain}] unkown. can't connect libra/violas node")

            for node in nodes:
                try:
                    if self.work() == False:
                        return result(error.FAILED, f"connect {chain} work stop")

                    self._logger.debug("try connect node({}) : host = {} port = {} validator={} faucet ={}".format( \
                            node.get("name", ""), node.get("host", "127.0.0.1"), node.get("port", 4001), node.get("validator", None), node.get("faucet", None)))
                    client = Client.new(host=node.get("host", "127.0.0.1"), \
                            port=node.get("port", 4001), \
                            faucet_file = node.get("faucet", None), \
                            timeout = node.get("timeout", 30), \
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

    def is_module_address(vclient, address):
        try:
            state = vclient.get_account_state(address).datas.is_published(address)
            ret = result(error.SUCCEED, datas = state) 
            print(f"]]] {state}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def has_module(vclient, address, module):
        try:
            state = vclient.get_account_state(address).datas.is_published(module)
            ret = result(error.SUCCEED, datas = state) 
        except Exception as e:
            ret = parse_except(e)
        return ret

    def publish_module(self, account,  is_blocking = True):
        try:
            self._logger.info(f"publish_module(account address={account.address_hex}, is_blocking={is_blocking})")
            seq = self.__client.publish_module(account, is_blocking=is_blocking)
            ret = result(error.SUCCEED) 
            self._logger.info(f"sequence: {seq}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def create_violas_coin(self, module_account, address,  is_blocking = True):
        try:
            self._logger.info("create_violas_coin(module_account={}, address={}, is_blocking={})".format(module_account.address.hex(), address, is_blocking))
            datas = self.__client.create_token(module_account, address)
            ret = result(error.SUCCEED, datas = datas) 
        except Exception as e:
            ret = parse_except(e)
        return ret

    def mint_platform_coin(self, address, amount, auth_key_prefix, is_blocking = True):
        try:
            self._logger.info("start mint_platform_coin(address={}, amount={}, auth_key_prefix={} is_blocking={})".format(address, amount, auth_key_prefix, is_blocking))
            self.__client.mint_coin(address, amount, auth_key_prefix = auth_key_prefix, is_blocking = is_blocking)
            ret = result(error.SUCCEED) 
        except Exception as e:
            ret = parse_except(e)
        return ret

    def bind_module(self, account, module_address, is_blocking=True):
        try:
            self._logger.info(f"start bind_module(account={account.address.hex}, module_address={module_address}, is_blocking={is_blocking}")
            self.__client.publish_resource(account, module_address, is_blocking=is_blocking)
            ret = result(error.SUCCEED) 
        except Exception as e:
            ret = parse_except(e)
        return ret

    def mint_violas_coin(self, address, amount, owner_account, token_id, module, auth_key_prefix = None, is_blocking=True):
        try:
            self._logger.info("start mint_violas_coin(address={}, amount={}, token_id={}, owner_account={}, auth_key_prefix={}, is_blocking={})".format(address, amount, token_id, owner_account.address.hex(), auth_key_prefix, is_blocking))
            self.__client.mint_coin(address, amount, owner_account, token_id, module, auth_key_prefix = auth_key_prefix, is_blocking=is_blocking)
            ret = result(error.SUCCEED) 
        except Exception as e:
            ret = parse_except(e)
        return ret

    def send_platform_coin(self, from_account, to_address, amount, data=None, is_blocking=True):
        try:
            self._logger.info(f"start send_platform_coin(from_account={from_account.address.hex()}, to_address={to_address}, amount={amount}, data={data}, is_blocking={is_blocking})")
            if len(to_address) != 64 or amount < 1:
                return result(error.ARG_INVALID)

            self.__client.transfer_coin(from_account, to_address, amount, data=data, is_blocking=is_blocking)
            ret = result(error.SUCCEED) 
        except Exception as e:
            ret = parse_except(e)
        return ret

    def send_violas_coin(self, from_account, to_address, amount, module_address, data=None, is_blocking=True):
        try:
            self._logger.info(f"start send_violas_coin(from_account={from_account.address.hex()}, to_address={to_address}, amount={amount}, module_address={module_address}, data={data}, is_blocking={is_blocking})")

            if len(to_address) != 64 or amount < 1 or len(module_address) != 64:
                return result(error.ARG_INVALID)

            if module_address == "0000000000000000000000000000000000000000000000000000000000000000":
                module_address = None

            self.__client.transfer_coin(sender_account=from_account, receiver_address=to_address, \
                    micro_coins=amount, module_address=module_address, data=data, is_blocking=is_blocking)
            ret = result(error.SUCCEED) 
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_platform_balance(self, account_address):
        try:
            self._logger.debug("get_platform_balance(address={})".format(account_address))
            balance = self.__client.get_balance(account_address)
            ret = result(error.SUCCEED, "", balance)
            self._logger.debug(f"resulst: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_violas_balance(self, account_address, module_address):
        try:
            self._logger.debug("get_balance(address={}, module={})".format(account_address, module_address))
            balance = self.__client.get_balance(account_address, module_address)
            ret = result(error.SUCCEED, "", balance)
            self._logger.debug(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_account_state(self, address):
        try:
            self._logger.debug("start get_account_state(address={})".format(address))
            state =  self.__client.get_account_state(address)
            ret = result(error.SUCCEED, "", state)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_address_sequence(self, address):
        try:
            self._logger.debug("start get_address_sequence(address={})".format(address))
            num = self.__client.get_account_sequence_number(address)
            ret = result(error.SUCCEED, "", num - 1)
            self._logger.debug(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_transaction_version(self, address, sequence):
        try:
            self._logger.debug(f"start get_transaction_version(address={address}, sequence={sequence})")
            num = self.__client.get_account_transaction(address, sequence).get_version()
            ret = result(error.SUCCEED, "", num)
            self._logger.debug(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret
    def get_address_version(self, address):
        try:
            self._logger.debug(f"start get_address_version(address={address})")
            ret = self.get_address_sequence(address)
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

    def get_scoin_resources(self, address):
        try:
            self._logger.debug(f"start get_scoin_resources(address={address})")
            vres = self.__client.get_account_state(address).get_scoin_resources().keys()
            ret = result(error.SUCCEED, "", list(vres))
            self._logger.debug(f"result: {len(ret.datas)}")
        except Exception as e:
            ret = parse_except(e)
        return ret
    def account_has_violas_module(self, address, module):
        try:
            self._logger.debug("start account_has_violas_module(address={}, module={})".format(address, module))
            vres = self.__client.get_account_state(address).get_scoin_resource(module)
            if vres is not None:
                ret = result(error.SUCCEED, "", True)
            else:
                ret = result(error.SUCCEED, "", False)
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
