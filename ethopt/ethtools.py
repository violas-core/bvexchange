#!/usr/bin/python3
import operator
import sys, getopt
import json
import os
sys.path.append(os.getcwd())
sys.path.append("..")
import log
import log.logger
import traceback
import datetime
import sqlalchemy
import stmanage
import requests
import comm
import comm.error
import comm.result
from comm.result import result
from comm.error import error
from comm.parseargs import parseargs
from comm.functions import json_print
from ethopt.ethclient import ethclient, ethwallet
from enum import Enum
from vrequest.request_client import requestclient
from analysis.analysis_filter import afilter
from dataproof import dataproof

#module name
name="ethtools"
chain = "ethereum"


#load logging
logger = log.logger.getLogger(name) 

'''
*************************************************ethclient oper*******************************************************
'''

def get_ethclient():

    client = ethclient(name, stmanage.get_eth_nodes(), chain)
    client.load_vlsmproof(stmanage.get_eth_token("vlsmproof")["address"])
    tokens = client.get_token_list().datas
    logger.debug(f"support tokens: {tokens}")
    for token in tokens:
        client.load_contract(token)
    return client
    

def get_ethwallet():
    return ethwallet(name, dataproof.wallets("ethereum"), chain)

def get_ethproof(dtype = "v2b"):

    return requestclient(name, stmanage.get_db(dtype))

def show_token_list(module):
    logger.debug(f"start show_token_name({module})")
    client = get_ethclient()
    ret = client.get_token_list(module)
    assert ret.state == error.SUCCEED, "get tokens failed."
    json_print(ret.datas)

def show_all_token_list():
    logger.debug(f"start show_all_token_list()")
    client = get_ethclient()
    ret = client.get_token_list()
    assert ret.state == error.SUCCEED, "get tokens failed."
    json_print(ret.datas)

def mint_coin(address, amount, token_id, module):
    logger.debug("start min_coin({address}, {amount}, {token_id}, {module})")
    print(client.get_balance(address, token_id, module).datas)

def bind_token_id(address, token_id, gas_token_id):
    logger.debug(f"start bind_token_id({address}, {token_id}, {gas_token_id}")

def send_coin(from_address, to_address, amount, token_id):
    wallet = get_ethwallet()
    ret = wallet.get_account(from_address)
    if ret.state != error.SUCCEED:
        raise Exception("get account failed")
    account = ret.datas

    client = get_ethclient()
    ret = client.send_coin_erc20(account, to_address, amount, token_id)
    assert ret.state == error.SUCCEED, ret.message
    print(f"cur balance :{client.get_balance(account.address, token_id).datas}")

def get_balance(address, token_id, module):
    logger.debug(f"start get_balance address= {address} module = {module} token_id= {token_id}")
    client = get_ethclient()
    ret = client.get_balance(address, token_id, module)
    logger.debug("balance: {0}".format(ret.datas))

def get_decimals(token_id):
    logger.debug(f"start get_decimals token_id= {token_id}")
    client = get_ethclient()
    ret = client.get_decimals(token_id)
    logger.debug("decimals: {0}".format(ret.datas))

def get_balances(address):
    logger.debug(f"start get_balances address= {address}")
    client = get_ethclient()
    ret = client.get_balances(address)
    logger.debug("balance: {0}".format(ret.datas))

def get_latest_transaction_version():
    logger.debug(f"start get_latest_transaction_version")
    client = get_ethclient()
    ret = client.get_latest_transaction_version()
    logger.debug("latest version: {0}".format(ret.datas))

def get_transactions(start_version, limit = 1, fetch_event = True, raw = False):
    logger.debug(f"start get_transactions(start_version={start_version}, limit={limit}, fetch_event={fetch_event})")

    client = get_ethclient()
    ret = client.get_transactions(start_version, limit, fetch_event)
    print(f"count: {len(ret.datas)}")
    if ret.state != error.SUCCEED:
        return
    if ret.datas is None or len(ret.datas) == 0:
        return
    for data in ret.datas:
        if raw:
            print(data)
        else:
            info = afilter.get_tran_data(data, chain =="violas")
            json_print(info)

def get_rawtransaction(txhash):
    logger.debug(f"start get_rawtransaction(txhash={txhash}")

    client = get_ethclient()
    ret = client.get_rawtransaction(txhash)
    if ret.state != error.SUCCEED:
        return

    print(ret.datas)
def get_address_version(address):
    logger.debug(f"start get_address_version({address})")
    client = get_ethclient()
    ret = client.get_address_version(address)
    logger.debug("version: {0}".format(ret.datas))

def get_address_sequence(address):
    logger.debug(f"start get_address_sequence({address})")
    client = get_ethclient()
    ret = client.get_address_sequence(address)
    logger.debug("version: {0}".format(ret.datas))

def get_transaction_version(address, sequence):
    logger.debug(f"start get_address_version({address}, {sequence})")
    client = get_ethclient()
    ret = client.get_transaction_version(address, sequence)
    logger.debug("version: {0}".format(ret.datas))


def get_syncing_state():
    logger.debug(f"start get_syncing_state()")
    client = get_ethclient()
    ret = client.get_syncing_state()
    logger.debug("version: {0}".format(ret.datas))
'''
*************************************************ethwallet oper*******************************************************
'''
def new_account():
    wallet = get_ethwallet()
    ret = wallet.new_account()
    wallet.dump_wallet()
    assert ret.state == error.SUCCEED, "new_account failed"
    logger.debug("account address : {}".format(ret.datas.address))

def address_has_token_id(address, token_id):
    logger.debug(f"start address_has_token_id address= {address} module = {token_id}")
    client = get_ethclient()
    logger.debug(client.has_token_id(address, token_id).datas)

def show_accounts():
    wallet = get_ethwallet()
    i = 0
    account_count = wallet.get_account_count()
    print(f"account count: {account_count}")
    while True and i < account_count:
        ret = wallet.get_account(int(i))
        if ret.state != error.SUCCEED:
           break 
        account = ret.datas
        logger.debug(f"{i}: {account.address}")
        i += 1

def show_accounts_full():
    wallet = get_ethwallet()
    i = 0
    account_count = wallet.get_account_count()
    while True and i < account_count:
        ret = wallet.get_account(i)
        if ret.state != error.SUCCEED:
           break 
        account = ret.datas
        logger.debug(f"({i:03}): address: {account.address} privkey: {account.key.hex()}")
        i += 1

def get_account(address):
    client = get_ethclient()
    print(client.get_account_state(address).datas)

def has_account(address):
    wallet = get_ethwallet()
    logger.debug(wallet.has_account_by_address(address).datas)


'''
*************************************************main oper*******************************************************
'''
def init_args(pargs):
    pargs.append("help", "show arg list.")
    pargs.append("conf", "config file path name. default:bvexchange.toml, find from . and /etc/bvexchange/", True, "toml file", priority = 10)
    pargs.append("wallet", "inpurt wallet file or mnemonic", True, "file name/mnemonic", priority = 13, argtype = parseargs.argtype.STR)

    #wallet 
    pargs.append("new_account", "new account and save to local wallet.")
    pargs.append("get_account", "show account info.", True, ["address"])
    pargs.append("has_account", "has target account in wallet.", True, ["address"])
    pargs.append("show_accounts", "show all counts address list(local wallet).")
    pargs.append("show_accounts_full", "show all counts address list(local wallet) with privkey.")

    #client
    pargs.append("send_coin", "send token(erc20 coin) to target address", True, ["form_address", "to_address", "amount", "token_id"])
    pargs.append("get_balance", "get address's token(module) amount.", True, ["address", "token_id", "module"])
    pargs.append("get_balances", "get address's tokens.", True, ["address"])
    pargs.append("get_account_transactions", "get account's transactions from eth server.", True, ["mtype", "address", "start", "limit", "state=(start/end)"])
    pargs.append("has_transaction", "check transaction is valid from eth server.", True, ["mtype", "tranid"])
    pargs.append("get_transactions", "get transactions from eth nodes.", True, ["start version", "limit=1", "fetch_event=True"])
    pargs.append("get_rawtransaction", "get transaction from eth nodes.", True, ["txhash"])
    pargs.append("get_latest_transaction_version", "show latest transaction version.")
    pargs.append("get_address_version", "get address's latest version'.", True, ["address"])
    pargs.append("get_address_sequence", "get address's latest sequence'.", True, ["address"])
    pargs.append("get_transaction_version", "get address's version'.", True, ["address", "sequence"])
    pargs.append("show_token_list", "show token list.", True, ["address"])
    pargs.append("show_all_token_list", "show token list.")
    pargs.append("get_decimals", "get address's token decimals.", True, ["token_id"])
    pargs.append("get_syncing_state", "get chain syncing state.")

def run(argc, argv):
    try:
        logger.debug("start eth.main")
        pargs = parseargs()
        init_args(pargs)
        pargs.show_help(argv)

        opts, err_args = pargs.getopt(argv)
    except getopt.GetoptError as e:
        logger.error(e)
        sys.exit(2)
    except Exception as e:
        logger.error(e)
        sys.exit(2)

    #argument start for --
    if len(err_args) > 0:
        pargs.show_args()

    names = [opt for opt, arg in opts]
    pargs.check_unique(names)

    #--conf must be first
    for opt, arg in opts:
        if pargs.is_matched(opt, ["conf"]):
            stmanage.set_conf_env(arg)
        elif pargs.is_matched(opt, ["wallet"]):
            if not arg:
                pargs.exit_error_opt(opt)
            dataproof.wallets.update_wallet("ethereum", arg)

    if stmanage.get_conf_env() is None:
        stmanage.set_conf_env("../bvexchange.toml") 

    global chain
    for opt, arg in opts:
        
        if opt in ["--conf", "--wallet"]:
            continue
        
        if len(arg) > 0:
            count, arg_list = pargs.split_arg(opt, arg)

            print("opt = {}, arg = {}".format(opt, arg_list))
        if pargs.is_matched(opt, ["chain"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            chain = arg_list[0]
        elif pargs.is_matched(opt, ["send_coin"]):
            if len(arg_list) != 4:
                pargs.exit_error_opt(opt)
            send_coin(arg_list[0], arg_list[1], arg_list[2], arg_list[3])
        elif pargs.is_matched(opt, ["get_account"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            get_account(arg)
        elif pargs.is_matched(opt, ["has_account"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            has_account(arg)
        elif pargs.is_matched(opt, ["show_accounts"]):
            if len(arg) != 0:
                pargs.exit_error_opt(opt)
            show_accounts()
        elif pargs.is_matched(opt, ["show_accounts_full"]):
            if len(arg) != 0:
                pargs.exit_error_opt(opt)
            show_accounts_full()
        elif pargs.is_matched(opt, ["new_account"]):
            if len(arg) != 0:
                pargs.exit_error_opt(opt)
            ret = new_account()
        elif pargs.is_matched(opt, ["get_balance"]):
            if len(arg_list) not in [3, 2]:
                pargs.exit_error_opt(opt)
            module = None
            token_id = None
            if len(arg_list) == 2:
                token_id = arg_list[1]
            else:
                module = arg_list[2]
                token_id = arg_list[1]
            get_balance(arg_list[0],  token_id, module )
        elif pargs.is_matched(opt, ["get_balances"]):
            if len(arg_list) not in [1]:
                pargs.exit_error_opt(opt)
            get_balances(arg_list[0])
        elif pargs.is_matched(opt, ["get_account_transactions"]):
            if len(arg_list) < 2 or len(arg_list) > 5:
                pargs.exit_error_opt(opt)
            mtype = arg_list[0]
            receiver = arg_list[1]
            start = -1
            limit = 10
            state = "start"

            if len(arg_list) >= 3:
               start = int(arg_list[2])

            if len(arg_list) >= 4:
               limit = int(arg_list[3])

            if len(arg_list) >= 5:
                state = arg_list[4]

            get_account_transactions(mtype, receiver, start, limit, state)
        elif pargs.is_matched(opt, ["get_transactions"]):
            if len(arg_list) != 3 and len(arg_list) != 2 and len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            if len(arg_list) == 3:
                get_transactions(int(arg_list[0]), int(arg_list[1]), arg_list[2] in ("True"))
            elif len(arg_list) == 2:
                get_transactions(int(arg_list[0]), int(arg_list[1]))
            elif len(arg_list) == 1:
                get_transactions(int(arg_list[0]))
        elif pargs.is_matched(opt, ["get_rawtransaction"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            get_rawtransaction(arg_list[0])
        elif pargs.is_matched(opt, ["has_transaction"]):
            if len(arg_list) != 2:
                pargs.exit_error_opt(opt)
            has_transaction(arg_list[0], arg_list[1])
        elif pargs.is_matched(opt, ["address_has_token_id"]):
            if len(arg_list) != 2:
                pargs.exit_error_opt(opt)
            address_has_token_id(arg_list[0], arg_list[1])
        elif pargs.is_matched(opt, ["get_latest_transaction_version"]):
            get_latest_transaction_version()
        elif pargs.is_matched(opt, ["get_address_version"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            get_address_version(arg_list[0])
        elif pargs.is_matched(opt, ["get_address_sequence"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            get_address_sequence(arg_list[0])
        elif pargs.is_matched(opt, ["get_transaction_version"]):
            if len(arg_list) != 2:
                pargs.exit_error_opt(opt)
            get_transaction_version(arg_list[0], int(arg_list[1]))
        elif pargs.is_matched(opt, ["show_token_list"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            show_token_list(arg_list[0])
        elif pargs.is_matched(opt, ["show_all_token_list"]):
            show_all_token_list()
        elif pargs.is_matched(opt, ["get_decimals"]):
            if len(arg_list) not in [1]:
                pargs.exit_error_opt(opt)
            get_decimals(arg_list[0])
        elif pargs.is_matched(opt, ["get_syncing_state"]):
            get_syncing_state()
        else:
            raise Exception(f"not found matched opt{opt}")
    logger.debug("end manage.main")

if __name__ == "__main__":
    run(len(sys.argv) - 1, sys.argv[1:])
