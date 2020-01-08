#!/usr/bin/python3
import operator
import sys, getopt
import json
import os
sys.path.append(os.getcwd())
sys.path.append("{}/packages/libra-client".format(os.getcwd()))
sys.path.append("..")
sys.path.append("../packages/libra-client")

import libra
from libra import Client
from libra import WalletLibrary
from libra.json_print import json_print
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
from db.dbb2v import dbb2v
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from violasclient import violasclient, violaswallet, violasserver
from enum import Enum
from vrequest.violas_proof import violasproof

#module name
name="violastools"

#load logging
logger = log.logger.getLogger(name) 

wallet_name = "vwallet"
'''
*************************************************violasclient oper*******************************************************
'''
def get_violasclient():
    return violasclient(name, stmanage.get_violas_nodes())

def get_violaswallet():
    return violaswallet(name, wallet_name)

def get_violasproof(dtype = "v2b"):
    return violasproof(name, stmanage.get_db(dtype))

def mint_platform_coin(address, amount):
    logger.debug("start mcreate_violas_coin otform_coin = {} amount={}".format(address, address))
    client = violasclient(stmanage.get_violas_nodes())

    ret = client.mint_platform_coin(address, amount)
    assert ret.state == error.SUCCEED, "mint_platform_coin failed."

    json_print(client.get_account_state(address).datas.to_json())

def mint_violas_coin(address, amount, module):
    logger.debug("start mcreate_violas_coin otform_coin = {} amount={} module={}".format(address, amount, module))
    global wallet_name
    client = get_violasclient()
    wallet = get_violaswallet()
    ret = wallet.get_account(module)
    if ret.state != error.SUCCEED:
        logger.error(ret.datas)
        return

    module_account = ret.datas

    ret = client.mint_violas_coin(address, amount, module_account)
    assert ret.state == error.SUCCEED, "mint_platform_coin failed."

    json_print(client.get_account_state(address).datas.to_json())

def create_violas_coin(module):
    logger.debug("start create_violas_coin module = {}".format(module))
    global wallet_name
    wallet = get_violaswallet()
    ret = wallet.get_account(module)
    if(ret.state != error.SUCCEED):
        return
    account = ret.datas

    client = get_violasclient()

    ret = client.create_violas_coin(account)
    if(ret.state != error.SUCCEED):
        return

    json_print(client.get_account_state(account.address).datas.to_json())

def bind_module(address, module):
    logger.debug("start bind_module address= {} module = {}".format(address, module))
    global wallet_name
    wallet = get_violaswallet()
    client = get_violasclient()
    ret = wallet.get_account(address)
    if ret.state != error.SUCCEED:
        logger.debug("get account failed")
    account = ret.datas

    ret = client.bind_module(account, module)
    assert ret.state == error.SUCCEED
    json_print(client.get_account_state(account.address).datas.to_json())

def send_violas_coin(from_address, to_address, amount, module, data = None):
    global wallet_name
    wallet = get_violaswallet()
    ret = wallet.get_account(from_address)
    if ret.state != error.SUCCEED:
        logger.debug("get account failed")
    account = ret.datas

    client = get_violasclient()
    client.send_violas_coin(account, to_address, amount, module, data)
    json_print(client.get_account_state(account.address).datas.to_json())

def get_platform_balance(address):
    logger.debug("start get_platform_balance address= {}".format(address))
    client = get_violasclient()
    ret = client.get_platform_balance(address)
    logger.debug("balance: {0}".format(ret.datas))

def get_violas_balance(address, module):
    logger.debug("start get_violas_balance address= {} module = {}".format(address, module))
    client = get_violasclient()
    ret = client.get_violas_balance(address, module)
    logger.debug("balance: {0}".format(ret.datas))

def get_latest_transaction_version():
    logger.debug("start get_latest_transaction_version")
    client = get_violasclient()
    ret = client.get_latest_transaction_version()
    logger.debug("latest version: {0}".format(ret.datas))

def get_transactions(start_version, limit = 1, fetch_event = True):
    logger.debug(f"start get_transactions(start_version={start_version}, limit={limit}, fetch_event={fetch_event})")
    client = get_violasclient()
    ret = client.get_transactions(start_version, limit, fetch_event)
    if ret.state != error.SUCCEED:
        return
    if ret.datas is None or len(ret.datas) == 0:
        return
    print(f"count: {len(ret.datas)}")

    for data in ret.datas:
        json_print(data.to_json())

'''
*************************************************violaswallet oper*******************************************************
'''
def new_account():
    global wallet_name
    wallet = get_violaswallet()
    ret = wallet.new_account()
    assert ret.state == error.SUCCEED, "new_account failed"
    logger.debug("account address : {}".format(ret.datas.address.hex()))

def account_has_violas_module(address, module):
    logger.debug("start account_has_violas_module address= {} module = {}".format(address, module))
    client = get_violasclient()
    logger.debug(client.account_has_violas_module(address, module).datas)

def show_accounts():
    global wallet_name
    wallet = get_violaswallet()
    i = 0
    account_count = wallet.get_account_count()
    while True and i < account_count:
        ret = wallet.get_account(str(i))
        if ret.state != error.SUCCEED:
           break 
        account = ret.datas
        logger.debug("account.address({0}): {1}".format(i, account.address.hex()))
        i += 1

def get_account(address):
    client = get_violasclient()
    json_print(client.get_account_state(address).datas.to_json())

def has_account(address):
    global wallet_name
    wallet = get_violaswallet()
    logger.debug(wallet.has_account_by_address(address).datas)
'''
*************************************************violasserver oper*******************************************************
'''
def get_violas_server():
    return violasserver(stmanage.get_violas_servers())

def get_account_transactions(address, module, start, limit, state):
    logger.debug("start get_account_transactions address= {} module = {}, start={}".format(address, module, start))
    #server = get_violas_server()
    server = get_violasproof("v2b")
    if state == "start":
        ret = server.get_transactions_for_start(address, module, start, limit)
    elif state == "end":
        ret = server.get_transactions_for_end(address, module, start, limit)
    for tran in ret.datas:
        logger.debug(tran)
    
def has_transaction(address, module, baddress, sequence, amount, version, receiver):
    logger.debug("start has_transaction address= {} module = {}, baddress={}, sequence={}, amount={}, version={}, receiver={}".format(address, module, baddress, sequence, amount, version, receiver))
    #server = get_violas_server()
    server = get_violasproof("v2b")
    logger.debug(server.has_transaction(address, module, baddress, sequence, amount, version, receiver).datas)

    
'''
*************************************************main oper*******************************************************
'''
def init_args(pargs):
    pargs.append("help", "show arg list.")
    pargs.append("mint_platform_coin", "mint vtoken(amount) to target address.", True, ["address", "amount"])
    pargs.append("create_violas_coin", "create new token(module) in violas blockchain", True, ["module"])
    pargs.append("bind_module", "bind address to module.", True, ["address", "module"])
    pargs.append("mint_violas_coin", "mint some(amount) token(module) to target address.", True, ["address", "amount", "module"])
    pargs.append("send_violas_coin", "send token(coin) to target address", True, ["form_address", "to_address", "amount", "module", "data[default = None  ex: v2b:btc_address:<BTC ADDRESS>]"])
    pargs.append("new_account", "new account and save to local wallet.")
    pargs.append("get_account", "show account info.", True, ["address"])
    pargs.append("has_account", "has target account in wallet.", True, ["address"])
    pargs.append("show_accounts", "show all counts address list(local wallet).")
    pargs.append("get_violas_balance", "get address's token(module) amount.", True, ["address", "module"])
    pargs.append("get_platform_balance", "get address's platform coin amount.", True, ["address"])
    pargs.append("get_account_transactions", "get account's transactions from violas server.", True, ["address", "module", "start", "limit", "state=(start/end)"])
    pargs.append("has_transaction", "check transaction is valid from violas server.", True, ["address", "module", "btcaddress", "sequence", "amount","version", "receiver"])
    pargs.append("account_has_violas_module", "check address binded module.", True, ["address", "module"])
    pargs.append("get_transactions", "get transactions from violas nodes.", True, ["start version", "limit=1", "fetch_event=True"])
    pargs.append("get_latest_transaction_version", "show latest transaction version.")


def run(argc, argv):
    try:
        logger.debug("start violas.main")
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

    for opt, arg in opts:
        if len(arg) > 0:
            count, arg_list = pargs.split_arg(arg)

            print("opt = {}, arg = {}".format(opt, arg_list))
        if pargs.is_matched(opt, ["create_violas_coin"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            ret = create_violas_coin(arg_list[0])
        elif pargs.is_matched(opt, ["bind_module"]):
            if len(arg_list) != 2:
                pargs.exit_error_opt(opt)
            ret = bind_module(arg_list[0], arg_list[1])
        elif pargs.is_matched(opt, ["mint_platform_coin"]):
            if len(arg_list) != 2:
                pargs.exit_error_opt(opt)
            ret = mint_platform_coin(arg_list[0], int(arg_list[1]))
        elif pargs.is_matched(opt, ["mint_violas_coin"]):
            if len(arg_list) != 3:
                pargs.exit_error_opt(opt)
            ret = mint_violas_coin(arg_list[0], int(arg_list[1]), arg_list[2])
        elif pargs.is_matched(opt, ["send_violas_coin"]):
            if len(arg_list) != 4 and len(arg_list) != 5:
                pargs.exit_error_opt(opt)
            if len(arg_list) == 5:
                ret = send_violas_coin(arg_list[0], arg_list[1], int(arg_list[2]), arg_list[3], json.dumps(arg_list[4]))
            else:
                ret = send_violas_coin(arg_list[0], arg_list[1], int(arg_list[2]), arg_list[3])
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
        elif pargs.is_matched(opt, ["new_account"]):
            if len(arg) != 0:
                pargs.exit_error_opt(opt)
            ret = new_account()
        elif pargs.is_matched(opt, ["get_violas_balance"]):
            if len(arg_list) != 2:
                pargs.exit_error_opt(opt)
            get_violas_balance(arg_list[0], arg_list[1])
        elif pargs.is_matched(opt, ["get_platform_balance"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            get_platform_balance(arg)
        elif pargs.is_matched(opt, ["get_account_transactions"]):
            if len(arg_list) < 2 or len(arg_list) > 5:
                pargs.exit_error_opt(opt)

            receiver = arg_list[0]
            module = arg_list[1]
            start = -1
            limit = 10
            state = "start"

            if len(arg_list) >= 3:
               start = int(arg_list[2])

            if len(arg_list) >= 4:
               limit = int(arg_list[3])

            if len(arg_list) >= 5:
                state = arg_list[4]

            get_account_transactions(receiver, module, start, limit, state)
        elif pargs.is_matched(opt, ["get_transactions"]):
            if len(arg_list) != 3 and len(arg_list) != 2 and len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            if len(arg_list) == 3:
                get_transactions(int(arg_list[0]), int(arg_list[1]), arg_list[2] in ("True"))
            elif len(arg_list) == 2:
                get_transactions(int(arg_list[0]), int(arg_list[1]))
            elif len(arg_list) == 1:
                get_transactions(int(arg_list[0]))
        elif pargs.is_matched(opt, ["has_transaction"]):
            if len(arg_list) != 7:
                pargs.exit_error_opt(opt)
            has_transaction(arg_list[0], arg_list[1], arg_list[2], int(arg_list[3]), int(arg_list[4]), int(arg_list[5]), arg_list[6])
        elif pargs.is_matched(opt, ["account_has_violas_module"]):
            if len(arg_list) != 2:
                pargs.exit_error_opt(opt)
            account_has_violas_module(arg_list[0], arg_list[1])
        elif pargs.is_matched(opt, ["get_latest_transaction_version"]):
            get_latest_transaction_version()
        elif opt == '-s':
            logger.debug(arg)
    logger.debug("end manage.main")

if __name__ == "__main__":
    run(len(sys.argv) - 1, sys.argv[1:])
