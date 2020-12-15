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
from dataproof import dataproof

#module name
name="violastools"
chain = "violas"
datatype = "v2b"


#load logging
logger = log.logger.getLogger(name) 

'''
*************************************************violasclient oper*******************************************************
'''

def get_violasclient():
    if chain == "libra":
        return violasclient(name, stmanage.get_libra_nodes(), chain)

    return violasclient(name, stmanage.get_violas_nodes(), chain)

def get_violaswallet():
    return violaswallet(name, dataproof.wallets(chain), chain)

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

def mint_coin(address, amount, token_id, module = None):
    logger.debug("start min_coin({address}, {amount}, {token_id}, {module})")
    client = get_violasclient()
    wallet = get_violaswallet()

    ret = client.mint_coin(address, amount, token_id, module)
    assert ret.state == error.SUCCEED, "mint_coin failed."

    print(client.get_balance(address, token_id, module).datas)

def bind_token_id(address, token_id, gas_token_id):
    logger.debug(f"start bind_token_id({address}, {token_id}, {gas_token_id}")
    wallet = get_violaswallet()
    client = get_violasclient()

    ret = wallet.get_account(address)
    if ret.state != error.SUCCEED:
        raise Exception("get account failed")
    account = ret.datas

    ret = client.bind_token_id(account, token_id, gas_token_id)
    assert ret.state == error.SUCCEED
    print(client.get_account_state(address).datas)

def send_coin(from_address, to_address, amount, token_id, module = None, data = None):
    wallet = get_violaswallet()
    ret = wallet.get_account(from_address)
    if ret.state != error.SUCCEED:
        raise Exception("get account failed")
    account = ret.datas

    if not isinstance(data, str):
        data = json.dumps(data)

    client = get_violasclient()
    ret = client.send_coin(account, to_address, amount, token_id, module, data)
    assert ret.state == error.SUCCEED, ret.message
    print(f"cur balance :{client.get_balance(account.address, token_id, module).datas}")

def get_balance(address, token_id):
    logger.debug(f"start get_balance address= {address} token_id= {token_id}")
    client = get_violasclient()
    ret = client.get_balance(address, token_id, None)
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

    if isinstance(fetch_event, str):
        fetch_event = fetch_event == "True"

    if isinstance(raw, str):
        raw = raw == "True"

    client = get_violasclient()
    client.swap_set_owner_address(stmanage.get_swap_owner())
    client.swap_set_module_address(stmanage.get_swap_module())
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
            info = afilter.get_tran_data(data, chain =="violas")
            json_print(info)

def get_address_version(address):
    logger.debug(f"start get_address_version({address})")
    client = get_violasclient()
    ret = client.get_address_version(address)
    logger.debug("version: {0}".format(ret.datas))

def get_address_sequence(address):
    logger.debug(f"start get_address_sequence({address})")
    client = get_violasclient()
    ret = client.get_address_sequence(address)
    logger.debug("version: {0}".format(ret.datas))

def get_transaction_version(address, sequence):
    logger.debug(f"start get_transaction_version({address}, {sequence})")
    client = get_violasclient()
    ret = client.get_transaction_version(address, sequence)
    logger.debug("version: {0}".format(ret.datas))

def create_child_vasp_account(parent_vasp_address, child_address, auth_key_prefix):
    logger.debug(f"start create_child_vasp_account({parent_vasp_address}, {child_address}, {auth_key_prefix})")
    client = get_violasclient()
    wallet = get_violaswallet()
    parent_vasp_account = wallet.get_account(parent_vasp_address).datas
    assert parent_vasp_account is not None, f"get parent account(parent_vasp_address) failed"

    ret = client.create_child_vasp_account(parent_vasp_account, child_address, auth_key_prefix)
    logger.debug("result: {0}".format(ret.datas))

'''
*************************************************violas swap oper*******************************************************
'''
def show_swap_registered_tokens(module = None):
    client = get_violasclient()
    swap_set_module_ower(client, module = module)
    ret = client.swap_get_registered_tokens()
    print(ret.datas)
    #json_print(ret.to_json())


def swap(sender, token_in, token_out, amount_in, amount_out_min=0, module_address = None):
    client = get_violasclient()

    swap_set_module_ower(client, module = module_address)

    wallet = get_violaswallet()
    ret = wallet.get_account(sender)
    if ret.state != error.SUCCEED:
        raise Exception("get account failed")
    sender_account = ret.datas

    ret = client.swap(sender_account = sender_account,token_in = token_in, \
            token_out = token_out, amount_in = amount_in, amount_out_min = amount_out_min)

def check_is_swap_address(address):
    client = get_violasclient()
    print(client.swap_is_swap_address(address))


def swap_set_module_ower(client, module = None, owner = None):
    logger.debug(f"owner:{stmanage.get_swap_owner()}, module:{stmanage.get_swap_module()}")
    
    if module is None:
        client.swap_set_module_address(stmanage.get_swap_module())
        module = stmanage.get_swap_module()
    else:
        client.swap_set_module_address(module)

    if owner is None or module in ("00000000000000000000000000000001"):
        client.swap_set_owner_address(stmanage.get_swap_owner())
    else:
        client.swap_set_owner_address(owner)

def swap_get_output_amount(token_in, token_out, amount_in):
    logger.debug(f"start swap_get_output_amount({token_in}, {token_out}, {amount_in})")
    client = get_violasclient()
    swap_set_module_ower(client)
    ret = client.swap_get_output_amount(token_in, token_out, amount_in)
    logger.debug(f"out_amount: {ret.datas}")

def swap_get_liquidity_balances(address):
    logger.debug(f"start swap_get_liquidity_balances({address})")
    client = get_violasclient()
    swap_set_module_ower(client)
    ret = client.swap_get_liquidity_balances(address)
    logger.debug(f"out_amount: {ret.datas}")

def swap_remove_liquidity(address, token_a, token_b, liquidity):
    logger.debug(f"start swap_remove_liquidity({address}, {token_a}, {token_b}, {liquidity})")
    client = get_violasclient()
    wallet = get_violaswallet()
    ret = wallet.get_account(address)
    if ret.state != error.SUCCEED:
        raise Exception("get account failed")
        
    sender_account = ret.datas
    swap_set_module_ower(client)
    ret = client.swap_remove_liquidity(sender_account, token_a, token_b, liquidity)
    logger.debug(f"out_amount: {ret.datas}")

'''
*************************************************violaswallet oper*******************************************************
'''
def new_account():
    wallet = get_violaswallet()
    ret = wallet.new_account()
    wallet.dump_wallet()
    assert ret.state == error.SUCCEED, "new_account failed"
    logger.debug("account address : {}".format(ret.datas.address.hex()))

def address_has_token_id(address, token_id):
    logger.debug(f"start address_has_token_id address= {address} module = {token_id}")
    client = get_violasclient()
    logger.debug(client.has_token_id(address, token_id).datas)

def show_accounts():
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


def get_account_role_id(address):
    client = get_violasclient()
    role_alias = {2:"DD", 5:"PARENT_VASP", 6:"CHILD_VASP"}
    role_id = client.get_account_state(address).datas.get_role_id()
    print(f"role_id: {role_id} alias: {role_alias.get(role_id)}")

def has_account(address):
    wallet = get_violaswallet()
    logger.debug(wallet.has_account_by_address(address).datas)

def get_account_prefix(address):
    wallet = get_violaswallet()
    account = wallet.get_account(address).datas
    logger.debug(f"address: {account.address.hex()}, auth_key_prefix: {account.auth_key_prefix.hex()}")

def human_address(address):
    logger.debug(f"start human_address({address})")
    h_address = bytes.fromhex(address).decode().replace("\x00","00")
    logger.debug(f"human address: {h_address}")

def get_wallet_address(address):
    logger.debug(f"start get_wallet_address({address})")
    wallet = get_violaswallet()
    logger.debug(f"human address: {wallet.get_wallet_address(address)}")
'''
*************************************************violasserver oper*******************************************************
'''
def get_violas_server():
    return violasserver(stmanage.get_violas_servers())

def get_account_transactions(mtype, address, start = -1, limit = 10, state = "start"):
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
    pargs.append("chain", "work chain name(violas/libra, default : violas). must be first argument", True, ["chain=violas"], priority = 10)
    pargs.append("conf", "config file path name. default:bvexchange.toml, find from . and /etc/bvexchange/", True, "toml file", priority = 5)
    pargs.append("wallet", "inpurt wallet file or mnemonic", True, "file name/mnemonic", priority = 13, argtype = parseargs.argtype.STR)
    #wallet 
    pargs.append(new_account, "new account and save to local wallet.")
    pargs.append(get_account, "show account info.")
    pargs.append(get_account_role_id, "show account role id.")
    pargs.append(has_account, "has target account in wallet.")
    pargs.append(show_accounts, "show all counts address list(local wallet).")
    pargs.append(show_accounts_full, "show all counts address list(local wallet) with auth_key_prefix.")
    pargs.append(human_address, "show human address.")
    pargs.append(get_wallet_address, "get wallet address if address is dd address.")

    #client
    pargs.append(bind_token_id, "bind address to token_id.")
    pargs.append(mint_coin, "mint some(amount) token(module) to target address.")
    pargs.append(send_coin, "send token(coin) to target address")
    pargs.append(get_balance, "get address's token(module) amount.")
    pargs.append(get_balances, "get address's tokens.")
    pargs.append(get_account_transactions, "get account's transactions from violas server.")
    pargs.append(has_transaction, "check transaction is valid from violas server.")
    pargs.append(get_transactions, "get transactions from violas nodes.")
    pargs.append(get_latest_transaction_version, "show latest transaction version.")
    pargs.append(get_address_version, "get address's latest version.")
    pargs.append(get_address_sequence, "get address's latest sequence.")
    pargs.append(get_transaction_version, "get address's version.")
    pargs.append(show_token_list, "show token list.")
    pargs.append(show_all_token_list, "show token list.")
    pargs.append(get_account_prefix, "get account prefix.")
    pargs.append(address_has_token_id, "check account is published token_id.")
    pargs.append(create_child_vasp_account, "create child vasp account.")

    #swap opt
    pargs.append(show_swap_registered_tokens, "show registered tokens for module.")
    pargs.append(swap, "swap violas chain token.")
    pargs.append(check_is_swap_address, "check address is swap address.")
    pargs.append(swap_get_output_amount, "get swap out amount .")
    pargs.append(swap_get_liquidity_balances, "get swap liquidity balances .")
    pargs.append(swap_remove_liquidity, "remover swap liquidity .")


def run(argc, argv):
    global chain
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
    if stmanage.get_conf_env() is None:
        stmanage.set_conf_env("../bvexchange.toml") 

    
    for opt, arg in opts:

        arg_list = []
        if len(arg) > 0:
            count, arg_list = pargs.split_arg(opt, arg)

            print("opt = {}, arg = {}".format(opt, arg_list))
        if pargs.is_matched(opt, ["chain"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            chain = arg_list[0]
        elif pargs.is_matched(opt, ["conf"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            stmanage.set_conf_env(arg_list[0])
        elif pargs.is_matched(opt, ["wallet"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            dataproof.wallets.update_wallet(chain, arg_list[0])
        elif pargs.has_callback(opt):
            pargs.callback(opt, *arg_list)
        else:
            raise Exception(f"not found matched opt: {opt}")


    logger.debug("end manage.main")

if __name__ == "__main__":
    run(len(sys.argv) - 1, sys.argv[1:])
