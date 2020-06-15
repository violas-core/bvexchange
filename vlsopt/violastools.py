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
from db.dbb2v import dbb2v
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

def publish_module(module):
    logger.debug(f"start publish_module({module})")
    client = get_violasclient()
    wallet = get_violaswallet()

    ret = client.has_module(module, module)
    assert ret.state == error.SUCCEED, f"check ({module}) failed."
    if ret.datas:
        logger.debug(f"module({module} had published.)")
        return 

    ret = wallet.get_account(module)
    assert ret.state == error.SUCCEED, f"get account({module}) failed."
    account = ret.datas

    ret = client.publish_module(account)
    assert ret.state == error.SUCCEED, "publish module failed."

    print(client.get_account_state(module).datas)

def create_violas_coin(module, address, name = None):
    logger.debug("start create_violas_coin module = {module}, address = {address}, name = {name}")
    global wallet_name
    wallet = get_violaswallet()
    ret = wallet.get_account(module)
    if(ret.state != error.SUCCEED):
        return
    account = ret.datas

    client = get_violasclient()

    ret = client.create_violas_coin(account, address, name = None)
    if(ret.state != error.SUCCEED):
        return

    print(ret.datas)

def get_token_name(address, token_id):
    logger.debug(f"start get_token_name({address}, {token_id})")
    client = get_violasclient()
    ret = client.get_token_data(address, token_id)
    assert ret.state == error.SUCCEED, "get token data failed."
    print(ret.datas)

def get_token_id(address, token_name):
    logger.debug(f"start get_token_id({address}, {token_name})")
    client = get_violasclient()
    ret = client.get_token_id(address, token_name)
    assert ret.state == error.SUCCEED, "get token data failed."
    print(ret.datas)

def show_token_list(module):
    logger.debug(f"start show_token_name({module})")
    client = get_violasclient()
    ret = client.get_token_list(module)
    assert ret.state == error.SUCCEED, "get tokens failed."
    json_print(ret.datas)

def show_tokens_info(module):
    logger.debug(f"start show_tokens_info({module})")
    client = get_violasclient()
    ret = client.get_tokens_info(module)
    assert ret.state == error.SUCCEED, "get tokens info failed."
    json_print(ret.datas)

def show_address_tokens(address, module):
    logger.debug(f"start show_address_tokens({address}, {module})")
    client = get_violasclient()
    ret = client.get_tokens(address, module)
    assert ret.state == error.SUCCEED, "get tokens failed."
    print(ret.datas)

def get_token_num(address):
    logger.debug(f"start get_token_num({address})")
    client = get_violasclient()
    ret = client.get_token_num(address)
    assert ret.state == error.SUCCEED, "get token num failed."
    print(ret.datas)

def mint_platform_coin(address, amount):
    logger.debug(f"start mint_platform_coin({address}, {amount})")
    client = get_violasclient()

    ret = client.mint_platform_coin(address, amount)
    assert ret.state == error.SUCCEED, "mint_platform_coin failed."

    print(client.get_platform_balance(address).datas)

def mint_violas_coin(address, amount, owner, token_id, module):
    logger.debug("start min_violas_coin({address}, {amount}, {owner}, {token_id}, {module})")
    global wallet_name
    client = get_violasclient()
    wallet = get_violaswallet()
    ret = wallet.get_account(owner)
    if ret.state != error.SUCCEED:
        logger.error(ret.datas)
        return

    account = ret.datas

    ret = client.mint_violas_coin(address, amount, account, token_id, module)
    assert ret.state == error.SUCCEED, "mint_violas_coin failed."

    print(client.get_violas_balance(address, module, token_id).datas)

def bind_module(address, module):
    logger.debug(f"start bind_module address= {address} module = {module}")
    global wallet_name
    wallet = get_violaswallet()
    client = get_violasclient()

    ret = client.has_module(address, module)
    assert ret.state == error.SUCCEED, f"check ({module}) failed."
    if ret.datas:
        logger.debug(f"module({module} had published.)")
        return 

    ret = wallet.get_account(address)
    if ret.state != error.SUCCEED:
        logger.debug("get account failed")
    account = ret.datas

    ret = client.bind_module(account, module)
    assert ret.state == error.SUCCEED
    print(client.get_account_state(account.address).datas)

def send_violas_coin(from_address, to_address, amount, token_id, module, data = None):
    global wallet_name
    wallet = get_violaswallet()
    ret = wallet.get_account(from_address)
    if ret.state != error.SUCCEED:
        logger.debug("get account failed")
    account = ret.datas

    client = get_violasclient()
    client.send_violas_coin(account, to_address, amount, token_id, module, data)
    print(client.get_violas_balance(account.address, module, token_id).datas)

def send_platform_coin(from_address, to_address, amount, data = None):
    global wallet_name
    wallet = get_violaswallet()
    ret = wallet.get_account(from_address)
    if ret.state != error.SUCCEED:
        logger.debug("get account failed")
    account = ret.datas

    client = get_violasclient()
    ret = client.send_platform_coin(account, to_address, amount, data)
    assert ret.state == error.SUCCEED, ret.message
    #print(client.get_account_state(account.address).datas)
    print(client.get_platform_balance(account.address).datas)

def get_platform_balance(address):
    logger.debug("start get_platform_balance address= {}".format(address))
    client = get_violasclient()
    ret = client.get_platform_balance(address)
    logger.debug("balance: {0}".format(ret.datas))

def get_violas_balance(address, module, token_id):
    logger.debug("start get_violas_balance address= {address} module = {module} token_id= {token_id}")
    client = get_violasclient()
    ret = client.get_violas_balance(address, module, token_id)
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
        info = afilter.get_tran_data(data, chain=="violas")
        json_print(info)
        print("********************formt transaction****************************")
        #finfo = afilter.parse_tran(info).datas
        #json_print(finfo)

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

def account_has_violas_module(address, module):
    logger.debug("start account_has_violas_module address= {} module = {}".format(address, module))
    client = get_violasclient()
    logger.debug(client.has_module(address, module).datas)

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
    #wallet 
    pargs.append("new_account", "new account and save to local wallet.")
    pargs.append("get_account", "show account info.", True, ["address"])
    pargs.append("has_account", "has target account in wallet.", True, ["address"])
    pargs.append("show_accounts", "show all counts address list(local wallet).")
    pargs.append("show_accounts_full", "show all counts address list(local wallet) with auth_key_prefix.")

    #client
    pargs.append("publish_module", "publish new module'.", True, ["address"])
    pargs.append("mint_platform_coin", "mint vtoken(amount) to target address.", True, ["address", "amount"])
    pargs.append("create_violas_coin", "create new token(module, address) in violas blockchain", True, ["module", "address", "name"])
    pargs.append("bind_module", "bind address to module.", True, ["address", "module"])
    pargs.append("mint_violas_coin", "mint some(amount) token(module) to target address.", True, ["address", "amount", "owner", "token_id", "module"])
    pargs.append("send_violas_coin", "send token(coin) to target address", True, ["form_address", "to_address", "amount", "token_id", "module", "data[default = None  ex: "])
    pargs.append("send_platform_coin", "send platform coin to target address", True, ["form_address", "to_address", "amount", "data[default = None  ex: "])
    pargs.append("get_violas_balance", "get address's token(module) amount.", True, ["address", "module", "token_id"])
    pargs.append("get_platform_balance", "get address's platform coin amount.", True, ["address"])
    pargs.append("get_account_transactions", "get account's transactions from violas server.", True, ["address", "module", "start", "limit", "state=(start/end)"])
    pargs.append("has_transaction", "check transaction is valid from violas server.", True, ["address", "module", "btcaddress", "sequence", "amount","version", "receiver"])
    pargs.append("account_has_module", "check address binded module.", True, ["address", "module"])
    pargs.append("get_transactions", "get transactions from violas nodes.", True, ["start version", "limit=1", "fetch_event=True"])
    pargs.append("get_latest_transaction_version", "show latest transaction version.")
    pargs.append("chain", "work chain name(violas/libra, default : violas). must be first argument", True, ["chain=violas"])
    pargs.append("get_address_version", "get address's latest version'.", True, ["address"])
    pargs.append("get_transaction_version", "get address's version'.", True, ["address", "sequence"])
    pargs.append("get_token_name", "show token name.", True, ["address", "token_id"])
    pargs.append("get_token_id", "show token id.", True, ["address", "token_name"])
    pargs.append("get_token_num", "get token num.", True, ["address"])
    pargs.append("show_address_tokens", "show tokens info.", True, ["address", "module"])
    pargs.append("show_token_list", "show token list.", True, ["module"])
    pargs.append("get_account_prefix", "get account prefix.", True, ["address"])
    pargs.append("show_tokens_info", "show tokens info.", True, ["module"])
    pargs.append("conf", "config file path name. default:bvexchange.toml, find from . and /etc/bvexchange/", True, "toml file")


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
        stmanage.set_conf_env_default() 

    global chain
    for opt, arg in opts:
        if len(arg) > 0:
            count, arg_list = pargs.split_arg(arg)

            print("opt = {}, arg = {}".format(opt, arg_list))
        if pargs.is_matched(opt, ["create_violas_coin"]):
            if len(arg_list) != 3:
                pargs.exit_error_opt(opt)
            ret = create_violas_coin(arg_list[0], arg_list[1], arg_list[2])
        elif pargs.is_matched(opt, ["bind_module"]):
            if len(arg_list) != 2:
                pargs.exit_error_opt(opt)
            ret = bind_module(arg_list[0], arg_list[1])
        elif pargs.is_matched(opt, ["mint_platform_coin"]):
            if len(arg_list) != 2:
                pargs.exit_error_opt(opt)
            ret = mint_platform_coin(arg_list[0], int(arg_list[1]))
        elif pargs.is_matched(opt, ["mint_violas_coin"]):
            if len(arg_list) != 5:
                pargs.exit_error_opt(opt)
            ret = mint_violas_coin(arg_list[0], int(arg_list[1]), arg_list[2], int(arg_list[3]), arg_list[4])
        elif pargs.is_matched(opt, ["send_violas_coin"]):
            if len(arg_list) not in (5,6):
                pargs.exit_error_opt(opt)
            if len(arg_list) == 6:
                ret = send_violas_coin(arg_list[0], arg_list[1], int(arg_list[2]), int(arg_list[3]), arg_list[4], json.dumps(arg_list[5]))
            else:
                ret = send_violas_coin(arg_list[0], arg_list[1], int(arg_list[2]), int(arg_list[3]), arg_list[4])
        elif pargs.is_matched(opt, ["send_platform_coin"]):
            if len(arg_list) not in (3, 4):
                pargs.exit_error_opt(opt)
            data = None
            if len(arg_list) == 4:
                data = json.dumps(arg_list[3])
            ret = send_platform_coin(arg_list[0], arg_list[1], int(arg_list[2]), data)
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
        elif pargs.is_matched(opt, ["get_violas_balance"]):
            if len(arg_list) != 3:
                pargs.exit_error_opt(opt)
            get_violas_balance(arg_list[0], arg_list[1], int(arg_list[2]))
        elif pargs.is_matched(opt, ["get_platform_balance"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            get_platform_balance(arg)
        elif pargs.is_matched(opt, ["publish_module"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            publish_module(arg)
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
        elif pargs.is_matched(opt, ["account_has_module"]):
            if len(arg_list) != 2:
                pargs.exit_error_opt(opt)
            account_has_violas_module(arg_list[0], arg_list[1])
        elif pargs.is_matched(opt, ["get_latest_transaction_version"]):
            get_latest_transaction_version()
        elif pargs.is_matched(opt, ["chain"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            chain = arg_list[0]
        elif pargs.is_matched(opt, ["get_address_version"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            get_address_version(arg_list[0])
        elif pargs.is_matched(opt, ["get_transaction_version"]):
            if len(arg_list) != 2:
                pargs.exit_error_opt(opt)
            get_transaction_version(arg_list[0], int(arg_list[1]))
        elif pargs.is_matched(opt, ["get_token_name"]):
            if len(arg_list) != 2:
                pargs.exit_error_opt(opt)
            get_token_name(arg_list[0], int(arg_list[1]))
        elif pargs.is_matched(opt, ["get_token_id"]):
            if len(arg_list) != 2:
                pargs.exit_error_opt(opt)
            get_token_id(arg_list[0], arg_list[1])
        elif pargs.is_matched(opt, ["show_address_tokens"]):
            if len(arg_list) != 2:
                pargs.exit_error_opt(opt)
            show_address_tokens(arg_list[0], arg_list[1])
        elif pargs.is_matched(opt, ["show_token_list"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            show_token_list(arg_list[0])
        elif pargs.is_matched(opt, ["get_token_num"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            get_token_num(arg_list[0])
        elif pargs.is_matched(opt, ["get_account_prefix"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            get_account_prefix(arg_list[0])
        elif pargs.is_matched(opt, ["show_tokens_info"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            show_tokens_info(arg_list[0])
    logger.debug("end manage.main")

if __name__ == "__main__":
    run(len(sys.argv) - 1, sys.argv[1:])
