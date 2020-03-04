#!/usr/bin/python3
import operator
import sys
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
import random
import comm
import comm.error
import comm.result
from comm.result import result, parse_except
from comm.error import error
from db.dbb2v import dbb2v
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from enum import Enum
from baseobject import baseobject
from vlsopt.violasclient import violasclient, violaswallet
from vlsopt.violasproof  import violasproof
import stmanage
import redis
#module name
name="commfuns"
wallet_name="vwallet"

class violasreg(violasproof):
    def __init__(self, name, nodes, chain="violas"):
        violasproof.__init__(self, name, nodes, chain)

    def __del__(self):
        violasproof.__del__(self)


class walletreg(violaswallet):
    def __init__(self, name, wallet_name, chain="violas"):
        violaswallet.__init__(self, name, wallet_name, chain)

    def __del__(self):
        violaswallet.__del__(self)

def get_address_info(vclient, wclient, address):
    plat_balance = vclient.get_platform_balance(address)
    infos = {}
    infos["plat balance"] = plat_balance.datas
    infos["is module"] = is_module_address(vclient, address)
    infos["resources"] = vclient.get_scoin_resources(address).datas
    resources = infos.get("resources")
    if resources is not None:
        balances = {}
        for module in resources:
            balances[f"{module}"] = f"{vclient.get_violas_balance(address, module).datas}"
        infos["balances"] = balances
    return infos
    
def list_address_info(vclient, wclient, addresses, ret):
    for address in addresses:
        info = get_address_info(vclient, wclient, address)
        ret.update({address:info})

def mint_platform_coin_for_address(vclient, wclient, address, amount=1000000, newcoin = False):
    vclient._logger.debug(f"start mint_platform_coin_for_address({address}, {amount})")
    assert address is not None and len(address) == 64, f"address({address}) is invalid."
    
    new_amount = amount
    if newcoin == False:
        new_amount = 0
        ret = vclient.get_platform_balance(address)
        assert ret.state == error.SUCCEED, f"get platform balance({address}) failed."
        if amount > ret.datas:
            new_amount = amount - ret.datas
    else:
        assert amount is not None and amount > 0, f"amount({amount}) is invalid."

    if new_amount > 0:
        ret = vclient.mint_platform_coin(address, new_amount)
        assert ret.state == error.SUCCEED, f"mint_platform_coin({address}, {amount}) failed."

    vclient._logger.info(f"mint platform coin({address}, {new_amount})")

def create_token(vclient, wclient, address, amount = 1000000, newcoin = False):
    vclient._logger.debug(f"start create token {address}")
    assert address is not None and len(address) == 64, f"address({address}) is invalid."

    if is_module_address(vclient, address):
        vclient._logger.debug(f"address({address}) is a module")
        return 

    ret = wclient.has_account_by_address(address)
    assert ret.state == error.SUCCEED and ret.datas == True, f"not found address {address} in wallet"
   
    mint_platform_coin_for_address(vclient, wclient, address, amount, newcoin)

    ret = wclient.get_account(address)
    assert ret.state == error.SUCCEED, f"get_account({address}) failed"
    account = ret.datas 

    ret = vclient.create_violas_coin(account)
    assert ret.state == error.SUCCEED, f"create_violas_coin({address}) failed."

    ret = vclient.bind_module(account, address)
    assert ret.state == error.SUCCEED, f"bind_module({address}, {address}) failed."

    vclient._logger.info(f"new module: {address}")

def bind_module(vclient, wclient, address, module):
    vclient._logger.debug(f"start bind_module({address}, {module})")
    assert address is not None and len(address) == 64, f"address({address}) is invalid."
    assert module is not None and len(module) == 64, f"module({module}) is invalid."

    if has_module(vclient, address, module) == True:
       vclient._logger.debug(f"address[address] has module[{module}]")
       return

    #must have some platform coin 
    mint_platform_coin_for_address(vclient, wclient, address)

    ret = wclient.get_account(address)
    assert ret.state == error.SUCCEED, f"get account:{address} failed"
    account = ret.datas

    ret = vclient.bind_module(account, module)
    assert ret.state == error.SUCCEED, f"bind_module({address}, {module}) failed."

    vclient._logger.info(f"{address} bind module {module}")

def has_module(vclient, address, module):
    assert address is not None and len(address) == 64, f"address({address}) is invalid."
    assert module is not None and len(module) == 64, f"module({module}) is invalid."
    return vclient.get_account_state(address).datas.is_published(module)

def is_module_address(vclient, module):
    assert module is not None and len(module) == 64, f"module({module}) is invalid."
    return vclient.get_account_state(module).datas.has_module()

def mint_violas_coin(vclient, wclient, address, module, amount):
    vclient._logger.debug(f"start mint_violas_coin({address}, {module}, {amount})")
    assert address is not None and len(address) == 64, f"address({address}) is invalid."
    assert module is not None and len(module) == 64, f"module({module}) is invalid."
    assert amount > 0, f"amount({amount} must be > 0)"
    if has_module(vclient, address, module) == False:
        bind_module(vclient, wclient, address, module)

    ret = wclient.get_account(module)
    assert ret.state == error.SUCCEED, f"get_account({module}) failed."
    module_account = ret.datas 

    ret = vclient.mint_violas_coin(address, amount, module_account)
    assert ret.state == error.SUCCEED, f"mint_violas_coin({address}, {amount}, {module}) failed."
    vclient._logger.info(f"mint violas coin({address}, {module}, {amount})")

def address_list_bind_module(vclient, wclient, senders, module):
    vclient._logger.debug(f"start address_list_bind_module([{senders}] ,{module})")
    assert senders is not None and len(senders) > 0, f"senders is empty."
    for address in senders:
        assert address is not None and len(address) == 64, f"address({address}) is invalid."
    assert module is not None and len(module) == 64, f"module({module}) is invalid."
    for sender in senders:
        bind_module(vclient, wclient, sender, module)

def init_address_list(vclient, wclient, senders, module, minamount= 1000000000):
    vclient._logger.debug(f"start init_address_list(address, {module}, {minamount})")
    assert senders is not None and len(senders) > 0, f"senders is empty."
    for address in senders:
        assert address is not None and len(address) == 64, f"address({address}) is invalid."
    assert module is not None and len(module) == 64, f"module({module}) is invalid."
    assert minamount >= 0 or minamount is None, f"min amount({minamount} must be > 0)"

    #must bind one or more module
    address_list_bind_module(vclient, wclient, senders, module)

    #set address min coin is amount
    min_balance = minamount
    #mimt vbtc coin
    for sender in senders:
        ret = vclient.get_violas_balance(sender, module)
        assert ret.state == error.SUCCEED, f"get_violas_balance({sender}, {module}) failed."
        if minamount is not None and ret.datas < min_balance:
            mint_violas_coin(vclient, wclient, sender, module, min_balance - ret.datas)
            vclient._logger.debug(f"mint violas coin {min_balance - ret.datas}")

