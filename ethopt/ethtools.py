#!/usr/bin/python3
import operator
import sys, getopt
import json
import os
sys.path.append(os.getcwd())
sys.path.append("..")
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
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
from comm.functions import (
        json_print,
        root_path
        )
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

client = None

def get_ethclient(usd_erc20 = True):
    global client
    if client:
        return client

    client = ethclient(name, stmanage.get_eth_nodes(), chain)
    client.load_vlsmproof(stmanage.get_eth_token("vlsmproof")["address"])
    if usd_erc20:
        tokens = client.get_token_list().datas
        logger.debug(f"support tokens: {tokens}")
        for token in tokens:
            client.load_contract(token)
    return client
    
ewclient = None
def get_ethwallet():
    global ewclient
    if ewclient:
        return eclient
    ewclient = ethwallet(name, dataproof.wallets("ethereum"), chain)
    return ewclient

def get_ethproof(dtype = "v2b"):

    return requestclient(name, stmanage.get_db(dtype))

def show_token_list(module = None):
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

def show_proof_contract_address(name):
    logger.debug(f"start show_proof_contract_address({name})")
    client = get_ethclient()
    ret = client.get_proof_contract_address(name)
    assert ret.state == error.SUCCEED, "get proof contract failed."
    print(ret.datas)

def mint_coin(address, amount, token_id, module):
    logger.debug("start mint_coin({address}, {amount}, {token_id}, {module})")
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

def approve(from_address, to_address, amount, token_id):
    wallet = get_ethwallet()
    ret = wallet.get_account(from_address)
    if ret.state != error.SUCCEED:
        raise Exception("get account failed")
    account = ret.datas

    client = get_ethclient()
    ret = client.approve(account, to_address, amount, token_id)
    assert ret.state == error.SUCCEED, ret.message
    print(f"cur balance :{client.allowance(from_address, to_address, token_id).datas}")

def send_proof(from_address, token_id, datas):
    wallet = get_ethwallet()
    ret = wallet.get_account(from_address)
    if ret.state != error.SUCCEED:
        raise Exception("get account failed")
    account = ret.datas

    client = get_ethclient()
    
    ret = client.send_proof(account, token_id, datas)
    assert ret.state == error.SUCCEED, ret.message
    print(f"cur balance :{client.get_balance(account.address, token_id).datas}")

def allowance(from_address, to_address, token_id):
    client = get_ethclient()
    ret = client.allowance(from_address, to_address, token_id)
    assert ret.state == error.SUCCEED, ret.message
    print(f"allowance balance :{ret.datas}")

def get_balance(address, token_id, module):
    logger.debug(f"start get_balance address= {address} module = {module} token_id= {token_id}")
    client = get_ethclient()
    ret = client.get_balance(address, token_id, module)
    logger.debug("balance: {0}".format(ret.datas))

def get_decimals(token_id):
    logger.debug(f"start get_decimals token_id= {token_id}")
    client = get_ethclient()
    ret = client.get_decimals(token_id)
    logger.debug(f"decimals: {ret}")

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

def get_address_latest_version(address):
    logger.debug(f"start get_address_latest_version({address})")
    client = get_ethclient()
    ret = client.get_address_latest_version(address)
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

def get_chain_id():
    logger.debug(f"start get_chain_id()")
    client = get_ethclient(False)
    ret = client.get_chain_id()
    logger.debug("version: {0}".format(ret.datas))

def get_token_min_amount(token_id):
    logger.debug(f"start get_token_min_amount({token_id})")
    client = get_ethclient(False)
    ret = client.get_token_min_amount(token_id)
    logger.debug("amount: {0}".format(ret.datas))

def get_token_max_amount(token_id):
    logger.debug(f"start get_token_max_amount({token_id})")
    client = get_ethclient(False)
    ret = client.get_token_max_amount(token_id)
    logger.debug("amount: {0}".format(ret.datas))

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
    pargs.clear()
    pargs.append("help", "show arg list.")
    pargs.append("conf", "config file path name. default:bvexchange.toml, find from . and /etc/bvexchange/", True, "toml file", priority = 10)
    pargs.append("wallet", "inpurt wallet file or mnemonic", True, "file name/mnemonic", priority = 13, argtype = parseargs.argtype.STR)

    #wallet 
    pargs.append(new_account, "new account and save to local wallet.")
    pargs.append(get_account, "show account info.")
    pargs.append(has_account, "has target account in wallet.")
    pargs.append(show_accounts, "show all counts address list(local wallet).")
    pargs.append(show_accounts_full, "show all counts address list(local wallet) with privkey.")

    #client
    pargs.append(send_coin, "send token(erc20 coin) to target address")
    pargs.append(approve, "approve to_address use coin amount from from_address")
    pargs.append(allowance, "request to_address can use coin amount from from_address")
    pargs.append(send_proof, "send mapping proof")
    pargs.append(get_balance, "get address's token(module) amount.")
    pargs.append(get_balances, "get address's tokens.")
    pargs.append(get_transactions, "get transactions from eth nodes.")
    pargs.append(get_rawtransaction, "get transaction from eth nodes.")
    pargs.append(get_latest_transaction_version, "show latest transaction version.")
    pargs.append(get_address_latest_version, "get address's latest version'.")
    pargs.append(get_address_sequence, "get address's latest sequence'.")
    pargs.append(get_transaction_version, "get address's version'.")
    pargs.append(get_decimals, "get address's token decimals.")
    pargs.append(get_syncing_state, "get chain syncing state.",)
    pargs.append(get_chain_id, "get chain id.")
    pargs.append(get_token_min_amount, "get token min amount of main contract.")
    pargs.append(get_token_max_amount, "get token min amount of main contract.")
    pargs.append(show_token_list, "show token list.")
    pargs.append(show_all_token_list, "show token list.")
    pargs.append(show_proof_contract_address, "show proof main address(args = main datas state).")


def run(argc, argv, exit = True):
    try:
        logger.debug("start eth.main")
        pargs = parseargs(exit = exit)
        init_args(pargs)
        pargs.show_help(argv)

        opts, err_args = pargs.getopt(argv)
    except getopt.GetoptError as e:
        logger.error(e)
        if exit:
            sys.exit(2)
        return 
    except Exception as e:
        logger.error(e)
        if exit:
            sys.exit(2)
        return 

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
        stmanage.set_conf_env(f"bvexchange.toml") 

    global chain
    for opt, arg in opts:
        
        if opt in ["--conf", "--wallet"]:
            continue
        
        arg_list = []
        if len(arg) > 0:
            count, arg_list = pargs.split_arg(opt, arg)

            print("opt = {}, arg = {}".format(opt, arg_list))
        if pargs.is_matched(opt, ["chain"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            chain = arg_list[0]
        elif pargs.is_matched(opt, ["get_transactions"]):
            if len(arg_list) != 3 and len(arg_list) != 2 and len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            if len(arg_list) == 3:
                get_transactions(int(arg_list[0]), int(arg_list[1]), arg_list[2] in ("True"))
            elif len(arg_list) == 2:
                get_transactions(int(arg_list[0]), int(arg_list[1]))
            elif len(arg_list) == 1:
                get_transactions(int(arg_list[0]))
        elif pargs.has_callback(opt):
            pargs.callback(opt, *arg_list)
        else:
            raise Exception(f"not found matched opt{opt}")
    logger.debug("end manage.main")

if __name__ == "__main__":
    run(len(sys.argv) - 1, sys.argv[1:])
