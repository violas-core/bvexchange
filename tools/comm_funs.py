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
import comm.values
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

VIOLAS_ADDRESS_LEN = comm.values.VIOLAS_ADDRESS_LEN
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

def get_address_info(vclient, wclient, address, module=None):
    plat_balance = vclient.get_platform_balance(address)
    infos = {}
    infos["plat balance"] = plat_balance.datas
    infos["is module"] = is_module_address(vclient, address)
    infos["module"] = module
    tokens = vclient.get_token_list(module).datas
    if module is not None:
        if tokens is not None:
            balances = {}
            for token_id in tokens:
                token_name = vclient.get_token_name(module, token_id).datas
                balances[f"{token_name}({token_id})"] = f"{vclient.get_violas_balance(address, module, token_id).datas}"
            infos["balances"] = balances
    return infos
    
def list_address_info(vclient, wclient, addresses, module, ret):
    for address in addresses:
        info = get_address_info(vclient, wclient, address, module)
        ret.update({address:info})

def publish_module(vclient, wclient, address):
    vclient._logger.debug(f"start publish_module({address})")
    assert address is not None and len(address) in VIOLAS_ADDRESS_LEN, f"address({address}) is invalid."

    ret = wclient.get_account(address)
    assert ret.state == error.SUCCEED, f"get account:{address} failed"
    account = ret.datas

    #must have some platform coin 
    mint_platform_coin_for_address(vclient, wclient, address, auth_key_prefix = account.auth_key_prefix)
    vclient.publish_module(account)

    ret = vclient.bind_module(account, address)
    assert ret.state == error.SUCCEED, f"bind_module({address}, {module}) failed."

def mint_platform_coin_for_address(vclient, wclient, address, amount=1000000, newcoin = False, auth_key_prefix=None):
    vclient._logger.debug(f"start mint_platform_coin_for_address({address}, {amount}, {auth_key_prefix})")
    assert address is not None and len(address) in VIOLAS_ADDRESS_LEN, f"address({address}) is invalid."
    
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
        ret = vclient.mint_platform_coin(address, new_amount, auth_key_prefix=auth_key_prefix)
        assert ret.state == error.SUCCEED, f"mint_platform_coin({address}, {amount}, {auth_key_prefix}) failed."

    ret = vclient.get_platform_balance(address)
    vclient._logger.info(f"mint platform coin({address}, {ret.datas}, {auth_key_prefix})")
    ret = vclient.get_platform_balance(address)
    vclient._logger.info(f"platform coin: {ret.datas}")


def create_token(vclient, wclient, address, module, name = None, amount = 1000000, newcoin = False):
    vclient._logger.debug(f"start create_token({address}, {module}, {amount}, {newcoin})")
    assert address is not None and len(address) in VIOLAS_ADDRESS_LEN, f"address({address}) is invalid."
    assert module is not None and len(module) in VIOLAS_ADDRESS_LEN, f"module({module}) is invalid."

    assert is_module_address(vclient, module) , f"{module} is not publish module"

    ret = wclient.has_account_by_address(module)
    assert ret.state == error.SUCCEED and ret.datas == True, f"not found module({module}) in wallet"

    ret = wclient.has_account_by_address(address)
    assert ret.state == error.SUCCEED and ret.datas == True, f"not found address({address}) in wallet"

    ret = wclient.get_account(module)
    assert ret.state == error.SUCCEED, f"get_account({module}) failed"
    module_account = ret.datas 

    ret = wclient.get_account(address)
    assert ret.state == error.SUCCEED, f"get_account({address}) failed"
    account = ret.datas 

    #make all address had platform coin and min count is amount(1000000)
    mint_platform_coin_for_address(vclient, wclient, address, amount, newcoin = newcoin, auth_key_prefix = account.auth_key_prefix)
    mint_platform_coin_for_address(vclient, wclient, module, amount, newcoin = newcoin, auth_key_prefix = module_account.auth_key_prefix)

    bind_module(vclient, wclient, address, module)

    ret = vclient.create_violas_coin(module_account, address, name=name)
    assert ret.state == error.SUCCEED, f"create_violas_coin({address}) failed."

    vclient._logger.info(f"create token ok: {address} {module} : {ret.datas}")
    return ret.datas

def bind_module(vclient, wclient, address, module):
    vclient._logger.debug(f"start bind_module({address}, {module})")
    assert address is not None and len(address) in VIOLAS_ADDRESS_LEN, f"address({address}) is invalid."
    assert module is not None and len(module) in VIOLAS_ADDRESS_LEN, f"module({module}) is invalid."

    if has_module(vclient, address, module) == True:
       vclient._logger.debug(f"address[address] has module[{module}]")
       return

    ret = wclient.get_account(address)
    assert ret.state == error.SUCCEED and ret.datas is not None, f"get account:{address} failed"
    account = ret.datas

    #must have some platform coin 
    mint_platform_coin_for_address(vclient, wclient, address, auth_key_prefix = account.auth_key_prefix)

    ret = vclient.bind_module(account, module)
    assert ret.state == error.SUCCEED, f"bind_module({address}, {module}) failed."

    vclient._logger.info(f"{address} bind module {module}")

def has_module(vclient, address, module):
    assert address is not None and len(address) in VIOLAS_ADDRESS_LEN, f"address({address}) is invalid."
    assert module is not None and len(module) in VIOLAS_ADDRESS_LEN, f"module({module}) is invalid."
    return vclient.has_module(address, module).datas

def is_module_address(vclient, module):
    assert module is not None and len(module) in VIOLAS_ADDRESS_LEN, f"module({module}) is invalid."
    return vclient.is_module_address(module).datas

def mint_violas_coin(vclient, wclient, receiver, amount, owner, token_id, module, auth_key_prefix = None):
    vclient._logger.debug(f"start mint_violas_coin({receiver}, {amount}, {owner}, {token_id}, {module}, {auth_key_prefix})")
    assert receiver is not None and len(receiver) in VIOLAS_ADDRESS_LEN, f"receiver({receiver}) is invalid."
    assert owner is not None and len(owner) in VIOLAS_ADDRESS_LEN, f"owner({owner}) is invalid."
    assert module is not None and len(module) in VIOLAS_ADDRESS_LEN, f"module({module}) is invalid."
    assert amount > 0, f"amount({amount} must be > 0)"
    if has_module(vclient, receiver, module) == False:
        bind_module(vclient, wclient, receiver, module)

    ret = wclient.get_account(owner)
    assert ret.state == error.SUCCEED, f"get_account({owner}) failed."
    owner_account = ret.datas 

    ret = vclient.mint_violas_coin(receiver, amount, owner_account, token_id, module, auth_key_prefix = auth_key_prefix)
    assert ret.state == error.SUCCEED, f"mint_violas_coin failed."
    vclient._logger.info(f"mint violas coin ok")

def address_list_bind_module(vclient, wclient, senders, module):
    vclient._logger.debug(f"start address_list_bind_module([{senders}] ,{module})")
    assert senders is not None and len(senders) > 0, f"senders is empty."
    for address in senders:
        assert address is not None and len(address) in VIOLAS_ADDRESS_LEN, f"address({address}) is invalid."
    assert module is not None and len(module) in VIOLAS_ADDRESS_LEN, f"module({module}) is invalid."
    for sender in senders:
        bind_module(vclient, wclient, sender, module)

def init_address_list(vclient, wclient, senders, owner, token_id, module, minamount= 1000000000):
    vclient._logger.debug(f"start init_address_list(address, {owner}, {token_id}, {module}, {minamount})")
    assert senders is not None and len(senders) > 0, f"senders is empty."
    for address in senders:
        assert address is not None and len(address) in VIOLAS_ADDRESS_LEN, f"address({address}) is invalid."
    assert module is not None and len(module) in VIOLAS_ADDRESS_LEN, f"module({module}) is invalid."
    assert owner is not None and len(owner) in VIOLAS_ADDRESS_LEN, f"owner({owner}) is invalid."
    assert minamount >= 0 or minamount is None, f"min amount({minamount} must be > 0)"

    #makesure address had platform balance
    mint_platform_coin_for_address(vclient, wclient, owner)
    for sender in senders:
        mint_platform_coin_for_address(vclient, wclient, sender)

    #must bind one or more module
    address_list_bind_module(vclient, wclient, senders, module)
    address_list_bind_module(vclient, wclient, [owner], module)


    #set address min coin is amount
    min_balance = minamount
    #mimt vbtc coin
    for sender in senders:
        ret = vclient.get_violas_balance(sender, module, token_id)
        assert ret.state == error.SUCCEED, f"get_violas_balance({sender}, {module}, {token_id}) failed."
        if minamount is not None and ret.datas < min_balance:
            mint_violas_coin(vclient, wclient, sender, min_balance - ret.datas, owner, token_id, module)
            vclient._logger.debug(f"mint violas coin {min_balance - ret.datas}")

        ret = vclient.get_violas_balance(sender, module, token_id)
        assert ret.state == error.SUCCEED, f"get_violas_balance({sender}, {module}, {token_id}) failed."
        vclient._logger.debug(f"mint_violas_coin result address: {sender}   violas coin token id:{token_id} balance: {ret.datas}   module:{module}")
