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

moudule = bytes.fromhex("cd0476e85ecc5fa71b61d84b9cf2f7fd524689a4f870c46d6a5d901b5ac1fdb2")
exg = violasclient(setting.traceback_limit)
def test_client():
    logger.debug("start test_conn")
    global wallet_name
    client = violasclient(setting.traceback_limit)
    ret = client.conn_node(setting.violas_nodes)
    if(ret.state != error.SUCCEED):
        return
    wallet = violaswallet(setting.traceback_limit)
    ret = wallet.load_wallet(wallet_name)

    vbtc = wallet.new_account().datas
    account = wallet.new_account().datas

    #mint platform coin to address
    client.mint_platform_coin(vbtc.address, 100)
    client.mint_platform_coin(account.address, 100)

    #create vbtc 
    client.create_violas_coin(vbtc)

    #bind to vbtc
    client.bind_module(vbtc, vbtc.address)
    client.bind_module(account, vbtc.address)

    #generate vbtc
    client.mint_violas_coin(vbtc.address, 100, vbtc)

    client.send_coins(vbtc, account.address, 10, vbtc.address)

    ret = client.get_balance(vbtc.address, vbtc.address)
    logger.debug("balance: {0}".format(ret.datas)) 

    logger.debug("account.address({0}): {1}".format(type(account.address), account.address.hex()))
    json_print(client.get_account_state(account.address).to_json())

def test_wallet():
    global wallet_name
    target_address_hex = "cd0476e85ecc5fa71b61d84b9cf2f7fd524689a4f870c46d6a5d901b5ac1fdb2"
    wallet = violaswallet(setting.traceback_limit, wallet_name)
    #ac1 = wallet.new_account()
    #ac2 = wallet.new_account()

    i = 0
    while i < 4:
        logger.debug("i = {}".format(i))
        ret = wallet.get_account(str(i))
        if ret.state != error.SUCCEED:
           break 
        account = ret.datas
        #logger.debug("account.address({0}): {1}".format(account.address, account.address.hex()))
        i += 1

    ret = wallet.get_account(target_address_hex)
    if ret.state == error.SUCCEED:
        logger.debug("found address:{}".format(target_address_hex))
    else:
        logger.debug("not found address:{}".format(target_address_hex))

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

    json_print(client.get_account_state(address).to_json())

def mint_violas_coin(address, amount, module):
    logger.debug("start mcreate_violas_coin otform_coin = {} amount={}".format(address, address))
    global wallet_name
    client = violasclient(setting.traceback_limit, setting.violas_nodes)
    wallet = violaswallet(setting.traceback_limit, wallet_name)
    ret = wallet.get_account(module)
    assert ret.state == error.SUCCEED, "get_account failed."
    module_account = ret.datas

    ret = client.mint_violas_coin(address, amount, module_account)
    assert ret.state == error.SUCCEED, "mint_platform_coin failed."

    json_print(client.get_account_state(address).to_json())

def create_violas_coin(module, amount):
    logger.debug("start create_violas_coin module = {} amount={}".format(module, amount))
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

    json_print(client.get_account_state(account.address).to_json())

def test_bind_one():    
    global wallet_name
    global moudule
    wallet = violaswallet(setting.traceback_limit, wallet_name)
    receiver = bytes.fromhex("210a283f13e42a37b7fb2dec50d8c2b28d6cc7e4f041fbdfa4998aa1b5663b89")
    client = violasclient(setting.traceback_limit)
    ret = client.conn_node(setting.violas_nodes)
    if(ret.state != error.SUCCEED):
        return

    ret = wallet.get_account(receiver.hex())
    if ret.state != error.SUCCEED:
        logger.debug("get account failed")
    account = ret.datas

    client.mint_platform_coin(moudule, 100000)
    client.mint_platform_coin(receiver, 100000)

    client.bind_module(account, moudule)
    client.mint_violas_coin(account.address, 10000, account)

    ret = client.get_balance(account, moudule)
    logger.debug("balance: {0}".format(ret.datas)) 
   
def test_mint_violas_coin():
    global module
    wallet = violaswallet(setting.traceback_limit, wallet_name)
    client = violasclient(setting.traceback_limit) 
    ret = client.conn_node(setting.violas_nodes)
    receiver = bytes.fromhex("210a283f13e42a37b7fb2dec50d8c2b28d6cc7e4f041fbdfa4998aa1b5663b89")
    address = bytes.fromhex("")
    if(ret.state != error.SUCCEED): 
        return
    ret = wallet.get_account(moudule.hex())
    if ret.state != error.SUCCEED:
        logger.debug("get account failed")
    module_account = ret.datas

    client.mint_platform_coin(receiver, 100000)
    client.mint_violas_coin(receiver, 100000, module_account)
    ret = client.get_balance(receiver, moudule)
    logger.debug("{} balance: {}".format(receiver.hex(), ret.datas)) 
   
def test_bind():
    global wallet_name
    global moudule
    wallet = violaswallet(setting.traceback_limit, wallet_name)
    moudule = bytes.fromhex("cd0476e85ecc5fa71b61d84b9cf2f7fd524689a4f870c46d6a5d901b5ac1fdb2")
    client = violasclient(setting.traceback_limit)
    ret = client.conn_node(setting.violas_nodes)
    if(ret.state != error.SUCCEED):
        return

    client.mint_platform_coin(moudule, 10000000)

    i = 0
    while True:
        logger.debug("i = {}".format(i))
        ret = wallet.get_account(str(i))
        if ret.state != error.SUCCEED:
           break 
        account = ret.datas
        logger.debug("account.address({0}): {1}".format(account.address, account.address.hex()))

        logger.debug("bind account{} to module {}".format(account.address, moudule))

        client.mint_platform_coin(account.address, 100000)
        client.bind_module(account, moudule)
        i += 1

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

def test_libra():
    print(sys.path)
    wallet = WalletLibrary.new()
    a1 = wallet.new_account()
    a2 = wallet.new_account()
    client = Client.new('18.220.66.235',40001, "consensus_peers.config.toml", "temp_faucet_keys")
    client.mint_coins(a1.address, 100, True)
    client.mint_coins(a2.address, 100, True)

    client.violas_publish(a1, True)
    client.violas_init(a1, a1.address, True)
    client.violas_init(a2, a1.address, True)
    client.violas_mint_coin(a1.address, 100, a1, True)
    print("before............")
    print("libra balance:", "a1=", client.get_balance(a1.address), "a2=", client.get_balance(a2.address))
    print("violas balance:", "a1=", client.violas_get_balance(a1.address, a1.address), "a2=", client.violas_get_balance(a2.address, a1.address))

    print("before:", client.violas_get_balance(a1.address, a1.address), client.violas_get_balance(a2.address, a1.address))
    client.violas_transfer_coin(a1, a2.address, 20, a1.address, is_blocking=True)
    print("after:", client.violas_get_balance(a1.address, a1.address), client.violas_get_balance(a2.address, a1.address))

def main(argc, argv):

       logger.debug("start main")
       #test_libra()
       #test_client()
       #test_wallet()
       #test_bind()
       #test_wallet_show()
       #test_bind_one()
       #test_new_account()
       #test_new_coin()
       test_mint_violas_coin()

args = {"help":"",
        "mint_platform_coin-":" mint_platform_coin address amount",
        "create_violas_coin-":"",
        "bind_module-":"",
        "mint_violas_coin-":"",
        "mint_platform_coin-":"",
        "get_account-":"",
        "has_account-":"",
        "show_accounts":"",
        "new_account":"",
        "get_violas_balance-":"",
        "get_platform_balance-":"",
        }
args_info = {
        }
def run(argc, argv):
    global args, args_info
    try:
        argfmt = list(args.keys())

        logger.debug("start violas.main")
        if argc == 0:
            logger.error([arg.replace('-', '') for arg in argfmt])
            sys.exit(2)
        opts, args = getopt.getopt(argv, "ha:b:s", [arg.replace('-', "=") for arg in argfmt])
    except getopt.GetoptError as e:
        logger.error(e)
        sys.exit(2)
    except Exception as e:
        logger.error(e)
        sys.exit(2)

    if len(args) > 0:
        logger.error("arguments format is invalid. {}".format([ "--" + arg.replace('-', "--") for arg in argfmt]))
    for opt, arg in opts:
        if len(arg) > 0:
            arg_list = "{}".format(arg).split(",")
            logger.debug("opt = {}, arg = {}".format(opt, arg_list))
        if opt in  ('-h', "--help"):
            logger.info("")
        elif opt in ("--create_violas_coin"):
            if len(arg_list) != 2:
                logger.error(args["create_violas_coin-"])
                sys.exit(2)
            ret = create_violas_coin(arg_list[0], int(arg_list[1]))
        elif opt in ("--bind_module"):
            logger.debug(arg)
        elif opt in ("--mint_platform_coin"):
            if len(arg_list) != 2:
                logger.error(args["mint_platform_coin-"])
                sys.exit(2)
            ret = mint_platform_coin(arg_list[0], int(arg_list[1]))
        elif opt in ("--mint_violas_coin"):
            if len(arg_list) != 3:
                logger.error(args["mint_violas_coin-"])
                sys.exit(2)
            ret = mint_violas_coin(arg_list[0], int(arg_list[1]), arg_list[2])
        elif opt in ("--get_account"):
            logger.debug(arg)
        elif opt in ("--has_account"):
            logger.debug(arg)
        elif opt in ("--show_accounts"):
            show_accounts()
        elif opt in ("--new_account"):
            ret = new_account()
        elif opt in ("--get_balance"):
            logger.debug(arg)
        elif opt == '-s':
            logger.debug(arg)
    logger.debug("end manage.main")

if __name__ == "__main__":
    run(len(sys.argv) - 1, sys.argv[1:])
