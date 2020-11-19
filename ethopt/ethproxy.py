#!/usr/bin/python3
import operator
import sys
import json
import os
sys.path.append("..")
import log
import log.logger
import traceback
import datetime
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
from enum import Enum
from comm.functions import json_print
from ethopt.vlsmproofmainslot import vlsmproofmainslot
from ethopt.vlsmproofdatasslot import vlsmproofdatasslot
from ethopt.vlsmproofstateslot import vlsmproofstateslot
from ethopt.erc20slot import erc20slot 
from ethopt.lbethwallet import lbethwallet
from dataproof import dataproof

import web3
from web3 import Web3

#module name
name="ethproxy"
import usdt_abi
import vmp_main_abi
import vmp_datas_abi
import vmp_state_abi

VLSMPROOF_MAIN_NAME = "vlsmproof"
VLSMPROOF_DATAS_NAME = "vmpdatas"
VLSMPROOF_STATE_NAME = "vmpstate"
contract_codes = {
        "usdt" : {"abi":usdt_abi.ABI, "bytecode":usdt_abi.BYTECODE, "token_type": "erc20", "address": usdt_abi.ADDRESS, "decimals": 6},
        VLSMPROOF_MAIN_NAME: {"abi": vmp_main_abi.ABI, "bytecode": vmp_main_abi.BYTECODE, "token_type": "main", "address":vmp_main_abi.ADDRESS},
        VLSMPROOF_DATAS_NAME: {"abi":vmp_datas_abi.ABI, "bytecode": vmp_datas_abi.BYTECODE, "token_type": "datas", "address":vmp_datas_abi.ADDRESS},
        VLSMPROOF_STATE_NAME: {"abi":vmp_state_abi.ABI, "bytecode": vmp_state_abi.BYTECODE, "token_type": "state", "address":vmp_state_abi.ADDRESS},
        }

class walletproxy(lbethwallet):
    @classmethod
    def load(self, filename):
        ret = self.recover(filename)
        return ret

    @classmethod
    def loads(self, data):
        ret = self.recover_from_mnemonic(data)
        return ret

    def find_account_by_address_hex(self, address):
        for i in range(self.child_count):
            if self.accounts[i].address == address:
                return (i, self.accounts[i])

        return (-1, None)

    def __getattr__(self, name):
        if name.startswith('__') and name.endswith('__'):
            raise AttributeError

class ethproxy():

    class transaction:
        def __init__(self, data):
            self._data = dict(data)

        def to_json(self):
            return self._data

        def get_version(self):
            return self._data["version"]

        def get_data(self):
            return self._data["data"]

    def clientname(self):
        return name
    
    def __init__(self, host, port, usd_chain = False, *args, **kwargs):
        self._w3 = None
        self.tokens_address = {}
        self.tokens_decimals = {}
        self.tokens = {}
        self.tokens_id = []
        self._vlsmproof_manager = None
        self.__usd_chain_contract_info = usd_chain

        self.connect(host, port, *args, **kwargs)
        self.load_vlsmproof(contract_codes[VLSMPROOF_MAIN_NAME]["address"]) #default, config will override

    def connect(self, host, port = None, *args, **kwargs):
        url = host
        if "://" not in host:
            url = f"http://{host}"
            if port is not None:
                url += f":{port}"

        self._w3 = Web3(Web3.HTTPProvider(url))

    def __init_contract_erc20(self):
        for token in contract_codes:
            self.load_contract(token)

    def __get_contract_info(self, name):
        contract = contract_codes[name]
        assert contract is not None, f"contract name({name}) is invalid."
        return contract

    def __get_token_decimals_with_name(self, erc20_token, name):
        contract = self.__get_contract_info(name)
        key = f"{name}_decimals"
        decimals= dataproof.configs(key)
        if decimals is None or decimals <= 0 or self.__usd_chain_contract_info:
            decimals = erc20_token.decimals()
            dataproof.configs.set_config(key, decimals)
        return decimals
        

    def __get_token_address_with_name(self, name):
        contract = self.__get_contract_info(name)
        key = f"{name}_address"
        address = dataproof.configs(key)
        #address = contract.get("address")
        if address is None or len(address) <= 0 or self.__usd_chain_contract_info:
            address = self.tokens[VLSMPROOF_MAIN_NAME].token_address(name)
            dataproof.configs.set_config(key, address)
        return address

    def __get_contract_address_with_name(self, vmpslot, name):
        contract = self.__get_contract_info(name)
        key = f"{name}_address"
        address = dataproof.configs(key)
        if address is None or len(address) <= 0 or self.__usd_chain_contract_info:
            if name == VLSMPROOF_DATAS_NAME:
                address = vmpslot.proof_address()
            elif name == VLSMPROOF_STATE_NAME:
                address = vmpslot.state_address()
            else:
                raise Exception(f"{name} is invalid.")

            dataproof.configs.set_config(key, address)
        return address

    def load_vlsmproof(self, address, name = VLSMPROOF_MAIN_NAME):
        '''
            load main  datas state
        '''
        if address == self.tokens_address.get(VLSMPROOF_MAIN_NAME, ""):
            return

        contract = contract_codes[name]
        if name == VLSMPROOF_MAIN_NAME:
            vmpslot = vlsmproofmainslot(self._w3.eth.contract(Web3.toChecksumAddress(address), abi=contract["abi"]))
            datas_address = self.__get_contract_address_with_name(vmpslot, VLSMPROOF_DATAS_NAME)
            self.load_vlsmproof(datas_address, VLSMPROOF_DATAS_NAME)
        elif name == VLSMPROOF_DATAS_NAME:
            vmpslot = vlsmproofdatasslot(self._w3.eth.contract(Web3.toChecksumAddress(address), abi=contract["abi"]))
            state_address = self.__get_contract_address_with_name(vmpslot, VLSMPROOF_STATE_NAME)
            self.load_vlsmproof(state_address, VLSMPROOF_STATE_NAME)
        elif name == VLSMPROOF_STATE_NAME:
            vmpslot = vlsmproofstateslot(self._w3.eth.contract(Web3.toChecksumAddress(address), abi=contract["abi"]))
        setattr(self, name, vmpslot)
        self.tokens_address[name] = address
        self.tokens[name] = vmpslot

    def load_contract(self, name):
        if name not in contract_codes:
            raise Exception(f"contract({name}) is invalid.")

        if name in (VLSMPROOF_MAIN_NAME, VLSMPROOF_DATAS_NAME, VLSMPROOF_STATE_NAME):
            return

        contract = contract_codes[name]
        address = self.__get_token_address_with_name(name)
        assert contract is not None, f"not support token({name})"
        erc20_token = erc20slot(self._w3.eth.contract(Web3.toChecksumAddress(address), abi=contract["abi"]))
        setattr(self, name, erc20_token)
        self.tokens_address[name] = address
        self.tokens_decimals[name] = pow(10, self.__get_token_decimals_with_name(erc20_token, name))
        self.tokens[name] = erc20_token
        self.tokens_id.append(name)

    def set_vlsmproof_manager(self, address):
        self._vlsmproof_manager = address

    def get_vlsmproof_manager(self, default = None):
        return self._vlsmproof_manager if self._vlsmproof_manager is not None else default

    def token_address(self, name):
        return self.tokens_address[name]

    def is_connected(self):
        return self._w3.isConnected()
    
    def syncing_state(self):
        return self._w3.eth.syncing

    def get_decimals(self, token):
        return self.tokens_decimals[token]

    def send_token(self, account, to_address, amount, token_id, nonce = None, timeout = 180):
        calldata = self.tokens[token_id].raw_transfer(to_address, amount)
        return self.send_transaction(account.address, account.key, calldata, nonce = nonce, timeout = 180) 

    def update_proof_state(self, account, version, state, timeout = 180):
        calldata = self.tokens[VLSMPROOF_DATAS_NAME].raw_transfer_proof_state_with_version(version, state)
        return self.send_transaction(account.address, account.key, calldata, nonce = version, timeout = timeout) 

    def send_transaction(self, sender, private_key, calldata, nonce = None, gas = None, gas_price = None, timeout = 180):

        if not gas_price:
            gas_price = self._w3.eth.gasPrice
        if not nonce:
            nonce = self._w3.eth.getTransactionCount(Web3.toChecksumAddress(sender))
        else:
            nonce = self._w3.eth.getTransactionCount(Web3.toChecksumAddress(sender))

        if not gas:
            gas = calldata.estimateGas({"from":sender})

        raw_tran = calldata.buildTransaction({
            "chainId": self.get_chain_id(),
            "gas" : gas,
            "gasPrice": gas_price,
            "nonce" : nonce
            })

        signed_txn = self._w3.eth.account.sign_transaction(raw_tran, private_key=private_key)
        txhash = self._w3.eth.sendRawTransaction(signed_txn.rawTransaction)

        #wait transaction, max time is 120s
        self._w3.eth.waitForTransactionReceipt(txhash, timeout)
        return self._w3.toHex(txhash)


    def call_default(self, *args, **kwargs):
        print(f"no defined function(args = {args} kwargs = {kwargs})")

    def block_number(self):
        return self._w3.eth.blockNumber

    def get_balance(self, address, token_id, *args, **kwargs):
        print(f"token_id:{token_id}, address: {address}")
        return self.tokens[token_id].balance_of(address)

    def get_balances(self, address, *args, **kwargs):
        balances = {}
        for token_id in self.tokens_id:
            balances.update({token_id: self.get_balance(address, token_id)})

        return balances

    def get_sequence_number(self, address):
        return self.tokens[VLSMPROOF_DATAS_NAME].proof_address_sequence(address)

    def token_name_list(self):
        return self.tokens[VLSMPROOF_MAIN_NAME].token_name_list()

    def get_account_transaction_version(self, address, sequence):
        return self.tokens[VLSMPROOF_DATAS_NAME].proof_address_version(address, sequence)

    def get_latest_version(self):
        return self.tokens[VLSMPROOF_DATAS_NAME].next_version()

    def create_std_metadata(self, datas):
        create = datas[6]
        metadata = {
                    "flag": "ethereum",
                    "type": f"e2vm",
                    "state": self.tokens[VLSMPROOF_STATE_NAME].state_name(datas[2]),
                    "opttype":"map",
                    "create" : create,
                    }
        if create:
            metadata.update({"to_address":datas[0], "out_amount": datas[5], "times":0})
        else:
            metadata.update({"tran_id":f"{datas[4]}_{datas[1]}"})
        return metadata

    def get_transactions(self, start, limit = 10, *args, **kwargs):
        return self._get_transactions(start, limit)

    def get_rawtransaction(self, txhash):
        return self._w3.eth.getTransaction(txhash)

    def get_chain_id(self):
        return self._w3.eth.chainId

    def _get_transactions(self, start, limit = 10):
        datas = []
        next_version = self.tokens[VLSMPROOF_DATAS_NAME].next_version()
        if next_version == 0:
            return datas
        assert start >= 0 and start < next_version and limit >= 1, "arguments is invalid"
        end = start + limit
        end = min(end - 1, next_version - 1)
        payee = self.tokens[VLSMPROOF_MAIN_NAME].payee()
        while start <= end:
            metadata = self.tokens[VLSMPROOF_DATAS_NAME].proof_info_with_version(start)
            data = self.create_std_metadata(metadata)
            datas.append(self.transaction(
                {
                    "token_id": self.tokens[VLSMPROOF_MAIN_NAME].token_name(metadata[3]),
                    "sender": metadata[4],
                    "receiver":self.tokens_address[VLSMPROOF_MAIN_NAME],
                    "amount": metadata[5],
                    "token_owner": metadata[3],
                    "sequence_number":metadata[1],
                    "version":start,
                    "data" : json.dumps(data).encode("utf-8").hex(),
                    "success" : True,
                    }
                ))
            start += 1
        return datas

    def __getattr__(self, name):
        if name.startswith('__') and name.endswith('__'):
            # Python internal stuff
            raise AttributeError
        raise Exception(f"not defined function:{name}")
        
    def __call__(self, *args, **kwargs):
        pass


def main():
    client = clientproxy.connect("")
    json_print(client.get_latest_version())
if __name__ == "__main__":
    main()
