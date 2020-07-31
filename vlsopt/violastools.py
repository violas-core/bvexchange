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
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from violasclient import violasclient, violaswallet, violasserver
from enum import Enum
from vrequest.request_client import requestclient
from analysis.analysis_filter import afilter

#module name
name="violastools"
chain = "violas"
datatype = "v2b"


#load logging
logger = log.logger.getLogger(name) 

wallet_name = "vwallet"
'''
*************************************************violasclient oper*******************************************************
'''

def get_violasclient():
    if chain == "libra":
        return violasclient(name, stmanage.get_libra_nodes(), chain)

    return violasclient(name, stmanage.get_violas_nodes(), chain)

def get_violaswallet():
    return violaswallet(name, wallet_name, chain)

def get_violasproof(dtype = "v2b"):

    return requestclient(name, stmanage.get_db(dtype))

def show_token_list(module):
    logger.debug(f"start show_token_name({module})")
    client = get_violasclient()
    ret = client.get_token_list(module)
    assert ret.state == error.SUCCEED, "get tokens failed."
    json_print(ret.datas)

def show_all_token_list():
    logger.debug(f"start show_all_token_list()")
    client = get_violasclient()
    ret = client.get_token_list()
    assert ret.state == error.SUCCEED, "get tokens failed."
    json_print(ret.datas)

def mint_coin(address, amount, token_id, module):
    logger.debug("start min_coin({address}, {amount}, {token_id}, {module})")
    global wallet_name
    client = get_violasclient()
    wallet = get_violaswallet()

    ret = client.mint_coin(address, amount, token_id, module)
    assert ret.state == error.SUCCEED, "mint_coin failed."

    print(client.get_balance(address, token_id, module).datas)

def bind_token_id(address, token_id, gas_token_id):
    logger.debug(f"start bind_token_id({address}, {token_id}, {gas_token_id}")
    global wallet_name
    wallet = get_violaswallet()
    client = get_violasclient()

    ret = wallet.get_account(address)
    if ret.state != error.SUCCEED:
        logger.debug("get account failed")
    account = ret.datas

    ret = client.bind_token_id(account, token_id, gas_token_id)
    assert ret.state == error.SUCCEED
    print(client.get_account_state(address).datas)

def send_coin(from_address, to_address, amount, token_id, module = None, data = None):
    global wallet_name
    wallet = get_violaswallet()
    ret = wallet.get_account(from_address)
    if ret.state != error.SUCCEED:
        logger.debug("get account failed")
    account = ret.datas

    if module is not None or len(module) == 0:
        module = None

    client = get_violasclient()
    client.send_coin(account, to_address, amount, token_id, module, data)
    print(f"cur balance :{client.get_balance(account.address, token_id, module).datas}")

def get_balance(address, token_id, module):
    logger.debug(f"start get_balance address= {address} module = {module} token_id= {token_id}")
    client = get_violasclient()
    ret = client.get_balance(address, token_id, module)
    logger.debug("balance: {0}".format(ret.datas))

def get_balances(address):
    logger.debug(f"start get_balances address= {address}")
    client = get_violasclient()
    ret = client.get_balances(address)
    logger.debug("balance: {0}".format(ret.datas))

def get_latest_transaction_version():
    logger.debug(f"start get_latest_transaction_version")
    client = get_violasclient()
    ret = client.get_latest_transaction_version()
    logger.debug("latest version: {0}".format(ret.datas))

def get_transactions(start_version, limit = 1, fetch_event = True, raw = False):
    logger.debug(f"start get_transactions(start_version={start_version}, limit={limit}, fetch_event={fetch_event})")

    client = get_violasclient()
    ret = client.get_transactions(start_version, limit, fetch_event)
    if ret.state != error.SUCCEED:
        return
    if ret.datas is None or len(ret.datas) == 0:
        return
    print(f"count: {len(ret.datas)}")

    for data in ret.datas:
        print(data.to_json())
        print("******")
        if raw:
            print(data)
        else:
            info = afilter.get_tran_data(data, chain=="violas")
            json_print(info)

def get_address_version(address):
    logger.debug(f"start get_address_version({address})")
    client = get_violasclient()
    ret = client.get_address_version(address)
    logger.debug("version: {0}".format(ret.datas))

def get_transaction_version(address, sequence):
    logger.debug(f"start get_address_version({address}, {sequence})")
    client = get_violasclient()
    ret = client.get_transaction_version(address, sequence)
    logger.debug("version: {0}".format(ret.datas))
'''
*************************************************violaswallet oper*******************************************************
'''
def new_account():
    global wallet_name
    wallet = get_violaswallet()
    ret = wallet.new_account()
    wallet.dump_wallet()
    assert ret.state == error.SUCCEED, "new_account failed"
    logger.debug("account address : {}".format(ret.datas.address.hex()))

def account_has_token_id(address, token_id):
    logger.debug(f"start account_has_token_id address= {address} module = {token_id}")
    client = get_violasclient()
    logger.debug(client.has_token_id(address, token_id).datas)

def show_accounts():
    global wallet_name
    wallet = get_violaswallet()
    i = 0
    account_count = wallet.get_account_count()
    print(f"account count: {account_count}")
    while True and i < account_count:
        ret = wallet.get_account(int(i))
        if ret.state != error.SUCCEED:
           break 
        account = ret.datas
        logger.debug("account.address({0}): {1}  auth_key_prefix: {2}".format(i, account.address.hex(), account.auth_key_prefix.hex()))
        i += 1

def show_accounts_full():
    global wallet_name
    wallet = get_violaswallet()
    i = 0
    account_count = wallet.get_account_count()
    while True and i < account_count:
        ret = wallet.get_account(i)
        if ret.state != error.SUCCEED:
           break 
        account = ret.datas
        logger.debug(f"({i:03}): {account.auth_key_prefix.hex()}{account.address.hex()}")
        i += 1
def get_account(address):
    client = get_violasclient()
    print(client.get_account_state(address).datas)

def has_account(address):
    global wallet_name
    wallet = get_violaswallet()
    logger.debug(wallet.has_account_by_address(address).datas)

def get_account_prefix(address):
    global wallet_name
    wallet = get_violaswallet()
    account = wallet.get_account(address).datas
    logger.debug(f"address: {account.address.hex()}, auth_key_prefix: {account.auth_key_prefix.hex()}")


def show_swap_registered_tokens(module):
    client = get_violasclient()
    client.swap_set_module_address(module)
    if module == "00000000000000000000000000000001":
        client.swap_set_owner_address("0000000000000000000000000a550c18")
    else:
        client.swap_set_owner_address(module)
    json_print(client.swap_get_registered_tokens().to_json())


def swap(sender_account, token_in, token_out, amount_in, amount_out_min=0, module_address = None, is_blocking=True):
    client = get_violasclient()
    client.set_exchange_module_address(module_address)
    ret = client.swap(sender_account = sender_account,token_in = token_in, \
            currency_out = token_out, amount_in = amount_in, amount_out_min = amount_out_min, \
            is_blocking = is_blocking)

def check_is_swap_address(address):
    client = get_violasclient()
    print(client.swap_is_swap_address(address))


'''
*************************************************violasserver oper*******************************************************
'''
def get_violas_server():
    return violasserver(stmanage.get_violas_servers())

def get_account_transactions(mtype, address, start, limit, state):
    logger.debug(f"start get_account_transactions({address}, {start}, {limit}, {state})")
    #server = get_violas_server()
    server = get_violasproof(mtype)
    if state == "start":
        ret = server.get_transactions_for_start(address, mtype, start, limit)
    elif state == "end":
        ret = server.get_transactions_for_end(address, mtype, start, limit)
    for tran in ret.datas:
        logger.debug(tran)
    
def has_transaction(mtype, tranid):
    logger.debug("start has_transaction({mtype}, {tranid})")
    #server = get_violas_server()
    server = get_violasproof(mtype)
    logger.debug(server.has_transaction(tranid).datas)

    
'''
*************************************************main oper*******************************************************
'''
def init_args(pargs):
    pargs.append("help", "show arg list.")
    pargs.append("chain", "work chain name(violas/libra, default : violas). must be first argument", True, ["chain=violas"])
    pargs.append("conf", "config file path name. default:bvexchange.toml, find from . and /etc/bvexchange/", True, "toml file")
    #wallet 
    pargs.append("new_account", "new account and save to local wallet.")
    pargs.append("get_account", "show account info.", True, ["address"])
    pargs.append("has_account", "has target account in wallet.", True, ["address"])
    pargs.append("show_accounts", "show all counts address list(local wallet).")
    pargs.append("show_accounts_full", "show all counts address list(local wallet) with auth_key_prefix.")

    #client
    pargs.append("bind_token_id", "bind address to token_id.", True, ["address", "token_id", "gas_token_id"])
    pargs.append("mint_coin", "mint some(amount) token(module) to target address.", True, ["address", "amount", "token_id", "module"])
    pargs.append("send_coin", "send token(coin) to target address", True, ["form_address", "to_address", "amount", "token_id", "module", "data[default = None  ex: "])
    pargs.append("get_balance", "get address's token(module) amount.", True, ["address", "token_id", "module"])
    pargs.append("get_balances", "get address's tokens.", True, ["address"])
    pargs.append("get_account_transactions", "get account's transactions from violas server.", True, ["mtype", "address", "start", "limit", "state=(start/end)"])
    pargs.append("has_transaction", "check transaction is valid from violas server.", True, ["mtype", "tranid"])
    pargs.append("get_transactions", "get transactions from violas nodes.", True, ["start version", "limit=1", "fetch_event=True"])
    pargs.append("get_rawtransaction", "get transaction from violas nodes.", True, ["version", "fetch_event=True"])
    pargs.append("get_latest_transaction_version", "show latest transaction version.")
    pargs.append("get_address_version", "get address's latest version'.", True, ["address"])
    pargs.append("get_transaction_version", "get address's version'.", True, ["address", "sequence"])
    pargs.append("show_token_list", "show token list.", True, ["address"])
    pargs.append("show_all_token_list", "show token list.")
    pargs.append("get_account_prefix", "get account prefix.", True, ["address"])
    pargs.append("account_has_token_id", "check account is published token_id.", True, ["address", "token_id"])
    pargs.append("swap", "swap violas chain token.", True, ["address", "token_in", "token_out", "amount_in", "amount_out_min", "module_address"])
    pargs.append("check_is_swap_address", "check address is swap address.", True, ["address"])


    #swap opt
    pargs.append("show_swap_registered_tokens", "show registered tokens for module.", True, ["address"])


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

    #--conf must be first
    for opt, arg in opts:
        if pargs.is_matched(opt, ["conf"]):
            stmanage.set_conf_env(arg)
            break
    if stmanage.get_conf_env() is None:
        stmanage.set_conf_env("../bvexchange.toml") 

    global chain
    for opt, arg in opts:
        
        if opt in ["--conf"]:
            continue
        
        if len(arg) > 0:
            count, arg_list = pargs.split_arg(arg)

            print("opt = {}, arg = {}".format(opt, arg_list))
        if pargs.is_matched(opt, ["chain"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            chain = arg_list[0]
        elif pargs.is_matched(opt, ["bind_token_id"]):
            if len(arg_list) != 3:
                pargs.exit_error_opt(opt)
            ret = bind_token_id(arg_list[0], arg_list[1], arg_list[2])
        elif pargs.is_matched(opt, ["mint_coin"]):
            if len(arg_list) != 4 and len(arg_list) != 3:
                pargs.exit_error_opt(opt)
            module = None
            if len(arg_list) == 4:
                module = arg_list[3]
            ret = mint_coin(arg_list[0], int(arg_list[1]), arg_list[2], module)
        elif pargs.is_matched(opt, ["send_coin"]):
            if len(arg_list) not in (4,5,6):
                pargs.exit_error_opt(opt)
            if len(arg_list) == 6:
                ret = send_coin(arg_list[0], arg_list[1], arg_list[2], arg_list[3], arg_list[4], json.dumps(arg_list[5]))
            elif len(arg_list) == 5:
                ret = send_coin(arg_list[0], arg_list[1], arg_list[2], arg_list[3], arg_list[4])
            elif len(arg_list) == 4:
                ret = send_coin(arg_list[0], arg_list[1], arg_list[2], arg_list[3])
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
            if len(arg_list) != 2 and len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            if len(arg_list) == 2:
                get_transactions(int(arg_list[0]), 1, arg_list[1] in ("True"), True)
            elif len(arg_list) == 1:
                get_transactions(int(arg_list[0]), 1, False, True)
        elif pargs.is_matched(opt, ["has_transaction"]):
            if len(arg_list) != 2:
                pargs.exit_error_opt(opt)
            has_transaction(arg_list[0], arg_list[1])
        elif pargs.is_matched(opt, ["account_has_token_id"]):
            if len(arg_list) != 2:
                pargs.exit_error_opt(opt)
            account_has_token_id(arg_list[0], arg_list[1])
        elif pargs.is_matched(opt, ["get_latest_transaction_version"]):
            get_latest_transaction_version()
        elif pargs.is_matched(opt, ["get_address_version"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            get_address_version(arg_list[0])
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
        elif pargs.is_matched(opt, ["get_account_prefix"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            get_account_prefix(arg_list[0])
        elif pargs.is_matched(opt, ["swap"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            get_account_prefix(arg_list[0])
        elif pargs.is_matched(opt, ["show_swap_registered_tokens"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            show_swap_registered_tokens(arg_list[0])
        elif pargs.is_matched(opt, ["check_is_swap_address"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            check_is_swap_address(arg_list[0])
        else:
            raise Exception(f"not found matched opt{opt}")
    logger.debug("end manage.main")

if __name__ == "__main__":
    run(len(sys.argv) - 1, sys.argv[1:])
