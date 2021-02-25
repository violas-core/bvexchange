#!/usr/bin/python3
import operator
import sys
import json
import os
sys.path.append("..")
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../lbdiemsdk/src"))
import requests
import typing

from diem import (
    diem_types, 
    jsonrpc, 
    utils, 
    chain_ids, 
    bcs, 
    stdlib, 
    identifier, 
    LocalAccount
        )

JSON_RPC_URL: str = "http://testnet.diem.com/v1"
FAUCET_URL: str = "http://testnet.diem.com/mint"
CHAIN_ID: diem_types.ChainId = chain_ids.TESTNET

DESIGNATED_DEALER_ADDRESS: diem_types.AccountAddress = utils.account_address("000000000000000000000000000000dd")
TEST_CURRENCY_CODE: str = "XUS"
HRP: str = identifier.TDM

class Faucet:
    """Faucet service is a proxy server to mint coins for your test account on Testnet

    See https://github.com/diem/diem/blob/master/json-rpc/docs/service_testnet_faucet.md for more details
    """

    def __init__(
        self,
        client: jsonrpc.Client,
        url: typing.Union[str, None] = None,
        retry: typing.Union[jsonrpc.Retry, None] = None,
    ) -> None:
        self._client: jsonrpc.Client = client
        self._url: str = url or FAUCET_URL
        self._retry: jsonrpc.Retry = retry or jsonrpc.Retry(5, 0.2, Exception)
        self._session: requests.Session = requests.Session()

    def gen_account(self, authkey, currency_code: str = TEST_CURRENCY_CODE, dd_account: bool = False) -> LocalAccount:
        self.mint(account.auth_key.hex(), 100_000_000_000, currency_code, dd_account)
        return account

    def mint(self, authkey: str, amount: int, currency_code: str, dd_account: bool = False) -> None:
        self._retry.execute(lambda: self._mint_without_retry(authkey, amount, currency_code, dd_account))

    def _mint_without_retry(self, authkey: str, amount: int, currency_code: str, dd_account: bool = False) -> None:
        response = self._session.post(
            FAUCET_URL,
            params={
                "amount": amount,
                "auth_key": authkey,
                "currency_code": currency_code,
                "return_txns": "true",
                "is_designated_dealer": "true" if dd_account else "false",
            },
        )
        response.raise_for_status()

        de = bcs.BcsDeserializer(bytes.fromhex(response.text))
        length = de.deserialize_len()

        for i in range(length):
            txn = de.deserialize_any(diem_types.SignedTransaction)
            self._client.wait_for_transaction(txn)
