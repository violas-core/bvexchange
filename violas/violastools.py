#!/usr/bin/python3
import operator
import sys, getopt
import json
import os
sys.path.append("..")
sys.path.append("../packages")
import libra
from libra import Client
from libra import WalletLibrary
from libra.json_print import json_print
import log
import log.logger
import traceback
import datetime
import sqlalchemy
import setting
import requests
import comm
import comm.error
import comm.result
from comm.result import result
from comm.error import error
from db.dbb2v import dbb2v
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from violasclient import violasclient, violaswallet
from enum import Enum

#module name
name="violasclient"

#load logging
logger = log.logger.getLogger(name) 

wallet_name = "vwallet"
def get_balance(address):
    client = violasclient(setting.traceback_limit, setting.nodes)
    ret = client.get_balance(vbtc.address, vbtc.address)
    logger.debug("balance: {0}".format(ret.datas)) 

def new_account():
    global wallet_name
    wallet = violaswallet(setting.traceback_limit, wallet_name)
    ret = wallet.new_account()
    assert ret.state == error.SUCCEED, "new_account failed"
    logger.debug("account address : {}".format(ret.datas.address.hex()))

def mint_platform_coin(address, amount):
    logger.debug("start mcreate_violas_coin otform_coin = {} amount={}".format(address, address))
    client = violasclient(setting.traceback_limit, setting.violas_nodes)

    ret = client.mint_platform_coin(address, amount)
    assert ret.state == error.SUCCEED, "mint_platform_coin failed."

    json_print(client.get_account_state(address).datas.to_json())

def mint_violas_coin(address, amount, module):
    logger.debug("start mcreate_violas_coin otform_coin = {} amount={} module={}".format(address, amount, module))
    global wallet_name
    client = violasclient(setting.traceback_limit, setting.violas_nodes)
    wallet = violaswallet(setting.traceback_limit, wallet_name)
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
    wallet = violaswallet(setting.traceback_limit, wallet_name)
    ret = wallet.get_account(module)
    if(ret.state != error.SUCCEED):
        return
    account = ret.datas

    client = violasclient(setting.traceback_limit, setting.violas_nodes)

    ret = client.create_violas_coin(account)
    if(ret.state != error.SUCCEED):
        return

    json_print(client.get_account_state(account.address).datas.to_json())

def bind_module(address, module):
    logger.debug("start bind_module address= {} module = {}".format(address, module))
    global wallet_name
    wallet = violaswallet(setting.traceback_limit, wallet_name)
    client = violasclient(setting.traceback_limit, setting.violas_nodes)
    ret = wallet.get_account(address)
    if ret.state != error.SUCCEED:
        logger.debug("get account failed")
    account = ret.datas

    ret = client.bind_module(account, module)
    assert ret.state == error.SUCCEED
    json_print(client.get_account_state(account.address).datas.to_json())

def send_coins(from_address, to_address, amount, module):
    global wallet_name
    wallet = violaswallet(setting.traceback_limit, wallet_name)
    ret = wallet.get_account(from_address)
    if ret.state != error.SUCCEED:
        logger.debug("get account failed")
    account = ret.datas

    client = violasclient(setting.traceback_limit, setting.violas_nodes)
    client.send_coins(account, to_address, amount, module)
    json_print(client.get_account_state(account.address).datas.to_json())

def get_balance(address, module):
    logger.debug("start get_balance address= {} module = {}".format(address, module))
    client = violasclient(setting.traceback_limit, setting.violas_nodes)
    ret = client.get_balance(address, module)
    logger.debug("balance: {0}".format(ret.datas))

def show_accounts():
    global wallet_name
    wallet = violaswallet(setting.traceback_limit, wallet_name)
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
    client = violasclient(setting.traceback_limit, setting.violas_nodes)
    json_print(client.get_account_state(address).datas.to_json())

def has_account(address):
    global wallet_name
    wallet = violaswallet(setting.traceback_limit, wallet_name)
    return wallet.has_account_by_address(address).datas

args = {"help"                  :   "dest: show arg list. format: --help",
        "mint_platform_coin-"   :   "dest: mint vtoken(amount) to target address.format: --mint_platform_coin \"address, amount\"",
        "create_violas_coin-"   :   "dest: create new token(module) in violas blockchain. format: --create_violas_coin \"module\"",
        "bind_module-"          :   "dest: bind address to module. format: --bind_module \"address, module\"",
        "mint_violas_coin-"     :   "dest: mint some(amount) token(module) to target address. format: --mint_violas_coin \"address, amount, module\" ",
        "send_coins-"           :   "dest: send token(coin) to target address. format: --send_coin \"form_address, to_address, amount, module\" ",
        "new_account"           :   "dest: new account and save to local wallet. format: --new_account",
        "get_account-"          :   "dest: show account info. format: --get_account \"address\"",
        "has_account-"          :   "dest: has target account in wallet. format: --has_account \"address\"",
        "show_accounts"         :   "dest: show all counts address list(local wallet).  foramt: --show_accounts",
        "get_violas_balance-"   :   "dest: get address's token(module) amount. format: --get_violas_balance \"address\"",
        "get_platform_balance-" :   "dest: get address's platform coin amount. fromat: --get_platform_balance \"address, module\"",
        }
args_info = {
        }

def show_args():
    global args
    for key in args.keys():
        print("{}{} \n\t\t\t\t{}".format("--", key.replace('-', ''), args[key].replace('\n', '')))

def exit_error_arg_list(arg):
    print(args["{}-".format(arg.replace('--', ''))])
    sys.exit(2)

def show_arg_info(info):
    print(info)

def run(argc, argv):
    global args, args_info
    try:
        argfmt = list(args.keys())

        logger.debug("start violas.main")
        if argc == 0:
            show_args()
            sys.exit(2)
        if argv[0] == "help" and argc == 2:
            if argv[1] in argfmt:
                show_arg_info("--{} \n\t{}".format(argv[1], args[argv[1]].replace("format:", "\n\tformat:")))
            else:
                show_arg_info("--{} \n\t{}".format(argv[1], args["{}-".format(argv[1])].replace("format:", "\n\tformat:")))
            sys.exit(2)

        opts, err_args = getopt.getopt(argv, "ha:b:s", [arg.replace('-', "=") for arg in argfmt])
    except getopt.GetoptError as e:
        logger.error(e)
        sys.exit(2)
    except Exception as e:
        logger.error(e)
        sys.exit(2)

    #argument start for --
    if len(err_args) > 0:
        show_arg_info("arguments format is invalid. {}".format([ "--" + arg.replace('-', "") for arg in argfmt]))

    for opt, arg in opts:
        if len(arg) > 0:
            arg_list = "{}".format(arg).split(",")
            
            arg_list = [sub.strip() for sub in arg_list]

            show_arg_info("opt = {}, arg = {}".format(opt, arg_list))
        if opt in ( "--help"):
            show_args()
            sys.exit(2)
        elif opt in ("--create_violas_coin"):
            if len(arg_list) != 1:
                show_arg_info(args["{}-".format(opt.replace('--', ''))])
                sys.exit(2)
            ret = create_violas_coin(arg_list[0])
        elif opt in ("--bind_module"):
            if len(arg_list) != 2:
                exit_error_arg_list(opt)
            ret = bind_module(arg_list[0], arg_list[1])
        elif opt in ("--mint_platform_coin"):
            if len(arg_list) != 2:
                exit_error_arg_list(opt)
            ret = mint_platform_coin(arg_list[0], int(arg_list[1]))
        elif opt in ("--mint_violas_coin"):
            if len(arg_list) != 3:
                exit_error_arg_list(opt)
            ret = mint_violas_coin(arg_list[0], int(arg_list[1]), arg_list[2])
        elif opt in ("--send_coins"):
            if len(arg_list) != 4:
                exit_error_arg_list(opt)
            ret = send_coins(arg_list[0], arg_list[1], int(arg_list[2]), arg_list[3])
        elif opt in ("--get_account"):
            if len(arg_list) != 1:
                exit_error_arg_list(opt)
            get_account(arg)
        elif opt in ("--has_account"):
            if len(arg_list) != 1:
                exit_error_arg_list(opt)
            has_account(arg)
        elif opt in ("--show_accounts"):
            if len(arg) != 0:
                exit_error_arg_list(opt)
            show_accounts()
        elif opt in ("--new_account"):
            if len(arg) != 0:
                exit_error_arg_list(opt)
            ret = new_account()
        elif opt in ("--get_violas_balance"):
            if len(arg_list) != 2:
                exit_error_arg_list(opt)
            get_violas_balance(arg_list[0], arg_list[1])
        elif opt in ("--get_platform_balance"):
            if len(arg_list) != 1:
                exit_error_arg_list(opt)
            get_plat_balance(arg)
        elif opt == '-s':
            logger.debug(arg)
    logger.debug("end manage.main")

if __name__ == "__main__":
    run(len(sys.argv) - 1, sys.argv[1:])
