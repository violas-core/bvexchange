#!/usr/bin/python3
import operator
import sys, getopt
import json
import os
sys.path.append(os.getcwd())
sys.path.append("..")
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
import datetime
import stmanage
import comm
import comm.error
import comm.result
from comm.result import result
from comm.error import error
from comm.parseargs import parseargs
from comm.functions import json_print
from vlsopt.violasclient import (
        violasclient, 
        violaswallet, 
        )
from enum import Enum
from analysis.analysis_filter import afilter
import analysis.parse_transaction as ptran
from dataproof import dataproof
chain = "diem"
name = "testdiemclient"
def get_violasclient():
    return violasclient(name, stmanage.get_target_nodes(chain), chain, use_faucet_file = True)

def get_violaswallet():
    return violaswallet(name, dataproof.wallets(chain), chain)

def test_show_token_list():
    client = get_violasclient()
    ret = client.get_token_list(None)
    assert ret.state == error.SUCCEED, "get tokens failed."
    json_print(ret.datas)


def test_get_balance():
    client = get_violasclient()
    ret = client.get_balance("af36eb657be8f8c20b773d1ffc290355", "XUS", None)
    assert ret.state == error.SUCCEED, "get balance failed."
    print("balance: {0}".format(ret.datas))


def test_get_balances():
    client = get_violasclient()
    ret = client.get_balances("af36eb657be8f8c20b773d1ffc290355")
    assert ret.state == error.SUCCEED, "get balances failed."
    print("balance: {0}".format(ret.datas))

def test_get_latest_version():
    client = get_violasclient()
    ret = client.get_latest_transaction_version()
    assert ret.state == error.SUCCEED, "get latest version failed."
    print("latest version: {0}".format(ret.datas))

def __show_transactions(datas, datatype):
    if datas is None or len(datas) == 0:
        print(f"count: {len(datas)}")
        return
    print(f"count: {len(datas)}")

    for data in datas:
        print(f"txn type: {type(data)}")
        if datatype == "raw":
            print(data)
        elif datatype in ["filter", "proof"]:
            print(f"******************{datatype}*********************************")
            info = afilter.get_tran_data(data, chain =="violas")
            if datatype in ["proof"]:
                info = ptran.parse_tran(info).datas
            json_print(info)

def test_get_transactions(start_version = 10000, limit = 1, fetch_event = True, datatype = "filter"):
    '''
    @dev get transaction and show info 
    @param datatype show data info type. raw: rawtransaction data of client, filter: filter will storage datas, proof: proof storage datas
    '''

    if isinstance(fetch_event, str):
        fetch_event = fetch_event in ["true", "True"]

    client = get_violasclient()
    client.swap_set_owner_address(stmanage.get_swap_owner())
    client.swap_set_module_address(stmanage.get_swap_module())
    ret = client.get_transactions(start_version, limit, fetch_event)
    assert ret.state == error.SUCCEED, "get transactions failed."

    __show_transactions(ret.datas, datatype)

def test_get_account_transactions(address = "af36eb657be8f8c20b773d1ffc290355", start = 1, limit = 1, fetch_event = True, datatype = "filter"):
    '''
    @dev get account transactions and show info 
    @param datatype show data info type. raw: rawtransaction data of client, filter: filter will storage datas, proof: proof storage datas
    '''

    if isinstance(fetch_event, str):
        fetch_event = fetch_event in ["true", "True"]

    client = get_violasclient()
    ret = client.get_account_transactions(address, start, limit, fetch_event)
    assert ret.state == error.SUCCEED, "get account transactions failed."

    __show_transactions(ret.datas, datatype)

def test_get_address_version(address = "af36eb657be8f8c20b773d1ffc290355"):
    client = get_violasclient()
    ret = client.get_address_version(address)
    assert ret.state == error.SUCCEED, "get account version failed."
    print("version: {0}".format(ret.datas))

def test_get_address_sequence(address = "af36eb657be8f8c20b773d1ffc290355"):
    client = get_violasclient()
    ret = client.get_address_sequence(address)
    assert ret.state == error.SUCCEED, "get account sequence failed."
    print("version: {0}".format(ret.datas))

def test_get_transaction_version(address = "af36eb657be8f8c20b773d1ffc290355", sequence = 0):
    client = get_violasclient()
    ret = client.get_transaction_version(address, sequence)
    assert ret.state == error.SUCCEED, "get transaction version failed."
    print("version: {0}".format(ret.datas))

client = None

def setup():
    client = get_violasclient()
    stmanage.set_conf_env("../bvexchange.toml")

if __name__ == "__main__":
    setup()
    pa = parseargs(globals())
    pa.test(sys.argv)
