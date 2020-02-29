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
import stmanage
import redis
#module name
name="regtoken"
wallet_name="vwallet"

logger = log.logger.getLogger(name)
class violasreg(violasclient):
    def __init__(self, name, nodes, chain="violas"):
        violasclient.__init__(self, name, nodes, chain)

    def __del__(self):
        violasclient.__del__(self)


class walletreg(violaswallet):
    def __init__(self, name, wallet_name, chain="violas"):
        violaswallet.__init__(self, name, wallet_name, chain)

    def __del__(self):
        violaswallet.__del__(self)

def create_token(vclient, wclient, address):
    logger.debug(f"start create token {address}")

    ret = wclient.has_account_by_address(address)
    assert ret.state == error.SUCCEED and ret.datas == True, f"not found address {address} in wallet"
   
    ret = vclient.get_platform_balance(address)
    assert ret.state == error.SUCCEED, f"get platform balance({address}) failed."

    if ret.datas < 1000000:
        ret = vclient.mint_platform_coin(address, amount)
        assert ret.state == error.SUCCEED, f"mint_platform_coin({address}, {amount}) failed."

    ret = wclient.get_account(address)
    assert ret.state == error.SUCCEED, f"get_account({address}) failed"
    account = ret.datas 

    ret = vclient.create_violas_coin(account)
    assert ret.state == error.SUCCEED, f"create_violas_coin({address}) failed."

    ret = vclient.bind_module(account, address)
    assert ret.state == error.SUCCEED, f"bind_module({address}, {address}) failed."

def bind_module(vclient, wclient, address, module):
    logger.debug(f"start bind_module({address}, {module})")
    ret = wclient.get_account(address)
    assert ret.state == error.SUCCEED, f"get account:{address} failed"
    account = ret.datas

    ret = vclient.bind_module(account, module)
    assert ret.state == error.SUCCEED, f"bind_module({address}, {module}) failed."

    logger.debug(f"{address} bind module {module}")

def has_module(vclient, address, module):
    return vclient.get_account_state(address).datas.is_published(module)

def is_module_address(vclient, module):
    return vclient.get_account_state(module).datas.has_module()

def mint_violas_coin(vclient, wclient, address, module, amount):
    logger.debug(f"start mint_violas_coin({address}, {module}, {amount})")
    if has_module(vclient, address, module) == False:
        bind_module(vclient, wclient, address, module)

    ret = wclient.get_account(module)
    assert ret.state == error.SUCCEED, f"get_account({module}) failed."
    module_account = ret.datas 

    ret = vclient.mint_violas_coin(address, amount, module_account)
    assert ret.state == error.SUCCEED, f"mint_violas_coin({address}, {amount}, {module}) failed."

def address_list_bind_module(vclient, wclient, senders, module):
    logger.debug(f"start address_list_bind_module({module})")
    for sender in senders:
        if has_module(vclient, sender, module) == False:
            bind_module(vclient, wclient, sender, module)
            logger.debug(f"address[sender] bind module[{module}]")
        else:
            logger.debug(f"address[sender] has module[{module}]")

def init_address_list(vclient, wclient, senders, module, coins = 1000000000):
    logger.debug(f"start init_address_list(address, {module}, {coins})")
    address_list_bind_module(vclient, wclient, senders, module)
    min_balance = coins
    #mimt vbtc coin
    for sender in senders:
        ret = vclient.get_violas_balance(sender, module)
        assert ret.state == error.SUCCEED, f"get_violas_balance({sender}, {module}) failed."
        if ret.datas < min_balance:
            mint_violas_coin(vclient, wclient, sender, module, min_balance - ret.datas)
            logger.debug(f"mint violas coin {min_balance - ret.datas}")

def reg_run():
    vclient = violasreg(name, stmanage.get_violas_nodes())
    wclient = walletreg(name, wallet_name)

    #create vbtc module
    vbtc_module = stmanage.get_module_address("v2b", "violas")
    assert vbtc_module is not None and len(vbtc_module) == 64, f"vbtc address[{vbtc_module}] is not found"

    if is_module_address(vclient, vbtc_module) == False:
        create_token(vclient, wclient, vbtc_module)
        logger.debug("create vbtc ok")
    else:
        logger.debug("vbtc is exists")


    #create vlibra module
    vlibra_module = stmanage.get_module_address("v2l", "violas")
    assert vbtc_module is not None and len(vbtc_module) == 64, "vlibra module is not found"

    if is_module_address(vclient, vlibra_module) == False:
        create_token(vclient, wclient, vlibra_module)
        logger.debug("create vlibra ok")
    else:
        logger.debug("vlibra is exists")


    #vbtc sender bind  module
    senders = stmanage.get_sender_address_list("b2v", "violas")
    assert senders is not None and len(senders) > 0, f"v2b senders[{senders}] not found."
    
    init_address_list(vclient, wclient, senders, vbtc_module)
    logger.debug("init b2v senders ok")

    #vlibra sender bind module
    senders = stmanage.get_sender_address_list("l2v", "violas")
    assert senders is not None and len(senders) > 0, f"v2l senders not found."
    logger.debug("init l2v senders ok")

    init_address_list(vclient, wclient, senders, vlibra_module)

    receivers = stmanage.get_receiver_address_list("v2l", "violas")
    assert receivers is not None and len(receivers) > 0, f"v2l receiver not found."
    address_list_bind_module(vclient, wclient, receivers, vlibra_module)

    receivers = stmanage.get_receiver_address_list("v2b", "violas")
    assert receivers is not None and len(receivers) > 0, f"v2b receiver not found."
    address_list_bind_module(vclient, wclient, receivers, vbtc_module)

    combins = stmanage.get_combine_address("v2b", "violas")
    assert combins is not None and len(combins) > 0, f"v2b combins not found."
    address_list_bind_module(vclient, wclient, combins, vbtc_module)

    combins = stmanage.get_combine_address("v2l", "violas")
    assert combins is not None and len(combins) > 0, f"v2l combins not found."
    address_list_bind_module(vclient, wclient, combins, vlibra_module)
if __name__ == "__main__":
    reg_run()
