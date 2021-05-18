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
from comm.functions import json_print
from vlsopt.violasclient import (
        violasclient, 
        violaswallet, 
        violasserver
        )
from enum import Enum
from vrequest.request_client import requestclient
from analysis.analysis_filter import afilter
import analysis.parse_transaction as ptran
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
        return violasclient(name, stmanage.get_libra_nodes(), chain, use_faucet_file = True)
    elif chain == "diem":
        return violasclient(name, stmanage.get_diem_nodes(), chain, use_faucet_file = True)

    print(stmanage.get_violas_nodes())
    return violasclient(name, stmanage.get_violas_nodes(), chain, use_faucet_file = True)

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

def get_latest_version():
    logger.debug(f"start get_latest_version")
    client = get_violasclient()
    ret = client.get_latest_transaction_version()
    logger.debug("latest version: {0}".format(ret.datas))

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

def get_transactions(start_version, limit = 1, fetch_event = True, datatype = "filter"):
    '''
    @dev get transaction and show info 
    @param datatype show data info type. raw: rawtransaction data of client, filter: filter will storage datas, proof: proof storage datas
    '''
    logger.debug(f"start get_transactions(start_version={start_version}, limit={limit}, fetch_event={fetch_event}, datatype = {datatype})")

    if isinstance(fetch_event, str):
        fetch_event = fetch_event in ["true", "True"]

    client = get_violasclient()
    client.swap_set_owner_address(stmanage.get_swap_owner())
    client.swap_set_module_address(stmanage.get_swap_module())
    ret = client.get_transactions(start_version, limit, fetch_event)
    if ret.state != error.SUCCEED:
        logger.debug(f"{ret.message}")
        return

    __show_transactions(ret.datas, datatype)

def get_account_transactions(address, start, limit = 1, fetch_event = True, datatype = "filter"):
    '''
    @dev get account transactions and show info 
    @param datatype show data info type. raw: rawtransaction data of client, filter: filter will storage datas, proof: proof storage datas
    '''
    logger.debug(f"start get_account_transactions(address = {address}, start={start}, limit={limit}, fetch_event={fetch_event}, datatype = {datatype})")

    if isinstance(fetch_event, str):
        fetch_event = fetch_event in ["true", "True"]

    client = get_violasclient()
    ret = client.get_account_transactions(address, start, limit, fetch_event)
    if ret.state != error.SUCCEED:
        logger.debug(f"{ret.message}")
        return

    __show_transactions(ret.datas, datatype)

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

def get_events(key, start = 0, limit = 10):
    client = get_violasclient()
    ret = client.get_events(key, start, limit)
    print(ret.datas)

def get_events_with_proof(key, start = 0, limit = 10):
    client = get_violasclient()
    ret = client.get_events_with_proof(key, start, limit)
    print(ret.datas)

def get_metadata(version = None):
    client = get_violasclient()
    ret = client.get_metadata(version)
    print(type(ret.datas))
    json_print(ret.datas.to_json())

def decode_address(address, chain_id = 2):
    wallet = get_violaswallet()
    addr, subaddr = wallet.decode_address(address, chain_id)
    print(f"addr:{addr.to_hex()} subaddr = {subaddr}")



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
*************************************************violas proof oper*******************************************************
'''
def get_account_transactions_with_state(mtype, address, start = -1, limit = 10, state = "start"):
    logger.debug(f"start get_account_transactions_with_state({address}, {start}, {limit}, {state})")
    server = get_violasproof(mtype)
    if state == "start":
        ret = server.get_transactions_for_start(address, mtype, start, limit)
    elif state == "end":
        ret = server.get_transactions_for_end(address, mtype, start, limit)
    for tran in ret.datas:
        logger.debug(tran)
    
def has_transaction(mtype, tranid):
    logger.debug("start has_transaction({mtype}, {tranid})")
    server = get_violasproof(mtype)
    logger.debug(server.has_transaction(tranid).datas)


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
    show_accounts_specify("std")

def show_accounts_specify(field, merge = False, with_human = False):
    wallet = get_violaswallet()
    i = 0
    account_count = wallet.get_account_count()
    print(f"account count: {account_count}")
    to_flag = "->" if with_human else ""
    while True and i < account_count:
        ret = wallet.get_account(int(i))
        if ret.state != error.SUCCEED:
           break 
        account = ret.datas
        human_addr = human_address(account.address.hex(), False) if with_human else ''
        if merge:
            print(f"account.address({i:02}): {account.auth_key_prefix.hex()}{account.address.hex()} {to_flag} {human_addr}")
        else:
            print(f"account.address({i:02}): address : {account.address_hex}  auth_key: {account.auth_key_prefix.hex()} {to_flag} {human_addr}")

        if field in ("all", "pri"):
            print(f"                   : pri__key: {account.private_key_hex}")
        elif field in ("all", "pub"):
            print(f"                   : pub__key: {account.public_key_hex}")

        i += 1


def show_accounts_full():
    show_accounts_specify("std", True)

def get_account(address):
    client = get_violasclient()
    print(client.get_account_state(address).datas)


def get_account_role_id(address):
    client = get_violasclient()
    role_alias = {2:"DD", 5:"PARENT_VASP", 6:"CHILD_VASP"}
    role_name = client.get_account_role_name(address).datas
    role_id= client.get_account_role_id(address).datas
    print(f"role_id: {role_id} alias: {role_name}")

def check_account_is_registered(address):
    client = get_violasclient()
    ret = client.check_account_is_registered(address)
    print(f"{address} registered: {ret.datas} ")

def has_account(address):
    wallet = get_violaswallet()
    logger.debug(wallet.has_account_by_address(address).datas)

def get_account_prefix(address):
    wallet = get_violaswallet()
    account = wallet.get_account(address).datas
    logger.debug(f"address: {account.address.hex()}, auth_key_prefix: {account.auth_key_prefix.hex()}")

def human_address(address, show = True):
    try:
        logger.debug(f"start human_address({address})") if show else ""
        h_address = bytes.fromhex(address).decode().replace("\x00","00")
    except Exception as e:
        print(e)
        h_address = address
    logger.debug(f"human address: {h_address}") if show else ""
    return h_address

def get_wallet_address(address):
    logger.debug(f"start get_wallet_address({address})")
    wallet = get_violaswallet()
    logger.debug(f"human address: {wallet.get_wallet_address(address)}")

def sign_message(address, message):
    wallet = get_violaswallet()
    logger.debug(f"human address: {wallet.sign_message(address, message)}")

'''
*************************************************violasserver oper*******************************************************
'''
def get_violas_server():
    return violasserver(name, stmanage.get_violas_servers())

def create_child_vasp_account_from_server(address, auth_key_prefix):
    logger.debug("start create_child_vasp_account_from_server({address}, {auth_key_prefix})")
    server = get_violas_server()
    logger.debug(server.create_child_vasp_account(address, auth_key_prefix).datas)
    
'''
*************************************************main oper*******************************************************
'''
def init_args(pargs):
    pargs.clear()
    pargs.append("help", "show arg list.")
    pargs.append("chain", "work chain name(violas/libra/diem, default : violas). must be first argument", True, ["chain=violas"], priority = 10)
    pargs.append("conf", "config file path name. default:bvexchange.toml, find from . and /etc/bridge/", True, "toml file", priority = 5)
    pargs.append("wallet", "inpurt wallet file or mnemonic", True, "file name/mnemonic", priority = 13, argtype = parseargs.argtype.STR)

    #wallet 
    pargs.append(new_account, "new account and save to local wallet.")
    pargs.append(get_account, "show account info.")
    pargs.append(get_account_role_id, "show account role id.")
    pargs.append(has_account, "has target account in wallet.")
    pargs.append(show_accounts, "show all counts address list(local wallet).")
    pargs.append(show_accounts_full, "show all counts address list(local wallet) with auth_key_prefix.")
    pargs.append(show_accounts_specify, "show all counts address list(local wallet) with specify field[all/pri/pub/std].")
    pargs.append(human_address, "show human address.")
    pargs.append(get_wallet_address, "get wallet address if address is dd address.")
    pargs.append(sign_message, "signing message.")
    pargs.append(decode_address, "decode address from identifier.")

    #client
    pargs.append(bind_token_id, "bind address to token_id.")
    pargs.append(mint_coin, "mint some(amount) token(module) to target address.")
    pargs.append(send_coin, "send token(coin) to target address")
    pargs.append(get_balance, "get address's token(module) amount.")
    pargs.append(get_balances, "get address's tokens.")
    pargs.append(get_account_transactions_with_state, "get account's transactions from violas server.")
    pargs.append(has_transaction, "check transaction is valid from violas server.")
    pargs.append(get_transactions, "get transactions from violas nodes. datatype = [filter | raw | proof]")
    pargs.append(get_account_transactions, "get account transactions from violas nodes. datatype = [filter | raw | proof]")
    pargs.append(get_latest_version, "show latest transaction version.")
    pargs.append(get_address_version, "get address's latest version.")
    pargs.append(get_address_sequence, "get address's latest sequence.")
    pargs.append(get_transaction_version, "get address's version.")
    pargs.append(show_token_list, "show token list.")
    pargs.append(show_all_token_list, "show token list.")
    pargs.append(get_account_prefix, "get account prefix.")
    pargs.append(address_has_token_id, "check account is published token_id.")
    pargs.append(create_child_vasp_account, "create child vasp account, make sure you are owner parent vasp .")
    pargs.append(check_account_is_registered, "check account is registered in violas/libra/diem chain.")
    pargs.append(get_events, "fetch the events for a given event stream.")
    pargs.append(get_events_with_proof, "fetch the events for a given event stream along with the necessary cryptographic proofs required to validate them.")
    pargs.append(get_metadata, "get the blockchain / ledger metadata")

    #swap opt
    #pargs.append(show_swap_registered_tokens, "show registered tokens for module.")
    #pargs.append(swap, "swap violas chain token.")
    #pargs.append(check_is_swap_address, "check address is swap address.")
    #pargs.append(swap_get_output_amount, "get swap out amount .")
    #pargs.append(swap_get_liquidity_balances, "get swap liquidity balances .")
    #pargs.append(swap_remove_liquidity, "remover swap liquidity .")

    #violas server
    pargs.append(create_child_vasp_account_from_server, "create child vasp account from violas server, you are't owner of parent vasp")

def run(argc, argv, exit = True):
    global chain
    try:
        logger.debug("start violas.main")
        pargs = parseargs(exit = exit)
        init_args(pargs)
        if pargs.show_help(argv):
            return 
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
    if err_args and len(err_args) > 0:
        pargs.show_args()
        return

    names = [opt for opt, arg in opts]
    pargs.check_unique(names)
    
    for opt, arg in opts:

        arg_list = []
        if len(arg) > 0:
            count, arg_list = pargs.split_arg(opt, arg)

            print("opt = {}, arg = {}".format(opt, arg_list))
        if pargs.is_matched(opt, ["chain"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            chain = arg_list[0]
        elif pargs.is_matched(opt, ["help"]):
            pargs.show_args()
            return
        elif pargs.is_matched(opt, ["conf"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            stmanage.set_conf_env(arg_list[0])
        elif pargs.is_matched(opt, ["wallet"]):
            pargs.exit_check_opt_arg(opt, arg, 1)
            dataproof.wallets.update_wallet(chain, arg_list[0])
        elif pargs.has_callback(opt):
            pargs.callback(opt, *arg_list)
        else:
            raise Exception(f"not found matched opt: {opt}")


    logger.debug("end manage.main")

if __name__ == "__main__":
    run(len(sys.argv) - 1, sys.argv[1:])
