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
from enum import Enum
from baseobject import baseobject
from vlsopt.violasclient import violasclient, violaswallet
from vlsopt.violasproof  import violasproof
import stmanage
import redis
from comm.functions import (
        json_print, 
        human_address
        )
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

def get_address_info(vclient, wclient, address):
    return  vclient.get_balances(address).datas
    
def has_tokens(vclient, wclient, address):
    balances = vclient.get_balances(address).datas
    return balances is not None and len(balances) > 0

def list_address_info(vclient, wclient, addresses, ret):
    if not addresses:
        return
    for address in addresses:
        info = get_address_info(vclient, wclient, address)
        ret.update({f"{address}->{human_address(address)}[{vclient.clientname()}]":info})

def get_gas_token_id(vclient, wclient, address, token_id, min_balance = 40_0000):
    vclient._logger.debug(f"start get_gas_token_id({address}, {token_id}, {min_balance})")
    ret = vclient.get_balances(address)
    for code, balance in ret.datas.items():
        if balance >= min_balance:
            return code

    return None

def bind_token_id(vclient, wclient, address, token_id, gas_token_id = None):
    vclient._logger.debug(f"start bind_token_id({address}, {token_id}, {gas_token_id})")
    assert address is not None and len(address) in VIOLAS_ADDRESS_LEN, f"address({address}) is invalid."

    if not vclient.token_id_effective(token_id):
        raise Exception(f"token id({token_id} is not registered.)")

    if has_token_id(vclient, address, token_id) == True:
       vclient._logger.debug(f"address[address] has token_id[{token_id}]")
       return

    ret = wclient.get_account(address)
    assert ret.state == error.SUCCEED and ret.datas is not None, f"get account:{address} failed"
    account = ret.datas

    if gas_token_id is None:
        gas_token_id = get_gas_token_id(vclient, wclient, address, token_id)

    ret = vclient.bind_token_id(account, token_id = token_id, gas_token_id = gas_token_id)
    assert ret.state == error.SUCCEED, f"bind_token_id({address}, {token_id}, {gas_token_id}) failed."

    vclient._logger.info(f"{address} bind token_id({token_id})")

def has_token_id(vclient, address, token_id):
    vclient._logger.debug(f"start has_token_id({address}] ,{token_id})")
    assert address is not None and len(address) in VIOLAS_ADDRESS_LEN, f"address({address}) is invalid."
    return vclient.has_token_id(address, token_id).datas

def mint_coin(vclient, wclient, funds_address, receiver, amount, token_id, auth_key_prefix = None, gas_token_id = None, debug = False):
    vclient._logger.debug(f"start mint_coin({receiver}, {amount}, {token_id}, {auth_key_prefix}, {gas_token_id}, {debug})")
    assert receiver is not None and len(receiver) in VIOLAS_ADDRESS_LEN, f"receiver({receiver}) is invalid."
    assert amount >= 0, f"amount({amount} must be > 0)"
    if has_tokens(vclient, wclient, receiver) and has_token_id(vclient, receiver, token_id) == False:
        vclient._logger.debug(f"bind token id({token_id})....")
        bind_token_id(vclient, wclient, receiver, token_id, gas_token_id)

    if amount > 0:
        if debug and token_id != "VLS":
            ret = vclient.mint_coin(receiver, amount, token_id, None)
        else:
            funds_account = wclient.get_account(funds_address).datas
            assert funds_account is not None, f"get parent account(funds_address) failed"
            ret = vclient.send_coin(funds_account, receiver, amount, token_id = token_id, auth_key_prefix = auth_key_prefix, gas_token_id = gas_token_id)
        assert ret.state == error.SUCCEED, f"mint_coin failed."
    vclient._logger.info(f"mint violas coin ok")

def address_list_bind_token_id(vclient, wclient, senders, token_id, gas_token_id = None):
    vclient._logger.debug(f"start address_list_bind_token_id([{senders}] ,{token_id}, {gas_token_id})")
    assert senders is not None and len(senders) > 0, f"senders is empty."
    for address in senders:
        assert address is not None and len(address) in VIOLAS_ADDRESS_LEN, f"address({address}) is invalid."
    for sender in senders:
        bind_token_id(vclient, wclient, sender, token_id, gas_token_id)

def create_child_vasp_account(vclient, wclient, parent_vasp_address, child_address, auth_key_prefix = None, gas_token_id = "VLS", child_initial_balance = 0):
    vclient._logger.debug(f"start create_child_vasp_account({parent_vasp_address}, {child_address}, {auth_key_prefix})")
    ret = vclient.check_account_is_registered(child_address)
    assert ret.state == error.SUCCEED, f"check account {child_address} registered state faild."
    if not ret.datas:
        parent_vasp_account = wclient.get_account(parent_vasp_address).datas
        assert parent_vasp_account is not None, f"get parent account(parent_vasp_address) failed"
        ret = vclient.create_child_vasp_account(parent_vasp_account, child_address, auth_key_prefix, gas_token_id = gas_token_id, child_initial_balance = child_initial_balance)
        assert ret.state == error.SUCCEED, f"registered {parent_vasp_address}'s child vasp account {child_address} faild."
        return ret
    vclient._logger.debug(f"account({child_address}) is registered.")
    return result(error.SUCCEED)

def create_child_vasp_account_remote(vclient, wclient, sclient, child_address, auth_key_prefix = None):
    vclient._logger.debug(f"start create_child_vasp_account_remote({child_address}, {auth_key_prefix})")
    ret = vclient.check_account_is_registered(child_address)
    assert ret.state == error.SUCCEED, f"check account {child_address} registered state faild."
    if not ret.datas:
        ret = sclient.create_child_vasp_account(child_address, auth_key_prefix)
        assert ret.state == error.SUCCEED, f"registered child vasp account {child_address} faild."
        return ret
    vclient._logger.debug(f"account({child_address}) is registered.")
    return result(error.SUCCEED)

def fill_token_id(vclient, wclient, from_address, to_address, gas_token_id = "VLS", amount = 1_00_0000):
    ret = vclient.check_account_is_registered(to_address)
    assert ret.state == error.SUCCEED, f"check account {address} registered state faild."
    if has_tokens(vclient, wclient, to_address) and has_token_id(vclient, to_address, token_id) == False:
        vclient._logger.debug(f"bind token id({token_id})....")
        bind_token_id(vclient, wclient, to_address, token_id, gas_token_id = "VLS")

    from_account = wclient.get_account(from_address).datas
    assert from_account is not None, f"get from account({from_address}) failed"
    ret = vclient.send_coin(from_account, to_address, amount, token_id = gas_token_id, gas_token_id = gas_token_id)
    return ret

def init_address_list(vclient, wclient, sclient, funds_address, senders, token_id, minamount= 0, gas_token_id = "VLS", debug = False):
    '''
    @dev init senders 
        operate:
        case 1. registered address of senders, if sender is not childvasp(default token is gas_token_id)
        case 2. bind token id(token id)
        case 3. fill token for sender
    @param vclient violas client
    @param wclient wallet client
    @param funds_address address of funds account  fill token to sender 
    @param senders operate addresses
    @param token_id init token_id
    @param minamount  inited token amount
    @param gas_token_id create_child_vasp_account or transfer gas token
    '''
    vclient._logger.debug(f"start init_address_list({senders}, {token_id}, {minamount})")
    assert senders is not None and len(senders) > 0, f"senders is empty."
    for address in senders:
        assert address is not None and len(address) in VIOLAS_ADDRESS_LEN, f"address({address}) is invalid."
    assert minamount >= 0 or minamount is None, f"min amount({minamount} must be > 0)"

    #set address min coin is amount
    min_balance = minamount
    #mimt vbtc coin
    for sender in senders:
        #check address(account) is registered
        ret = create_child_vasp_account_remote(vclient, wclient, sclient, sender)
        assert ret.state == error.SUCCEED, f"create_child_vasp_account_remote({sender}) failed."

        ret = vclient.get_balance(account_address = sender, token_id = token_id)
        assert ret.state == error.SUCCEED, f"get_balance({sender}, {token_id}) failed."
        cur_balance = ret.datas
        if cur_balance is None or (minamount is not None and cur_balance <= min_balance):
            if cur_balance is None:
                cur_balance = 0

            mint_coin(vclient, wclient, funds_address, sender, min_balance - cur_balance, token_id, auth_key_prefix = None, gas_token_id = gas_token_id, debug = debug)
            vclient._logger.debug(f"mint coin({token_id}) {min_balance - cur_balance}")

        ret = vclient.get_balance(sender, token_id = token_id)
        assert ret.state == error.SUCCEED, f"get_violas_balance({sender}, {token_id}) failed."
        vclient._logger.debug(f"mint_violas_coin result address: {sender}   violas coin token id:{token_id} balance: {ret.datas}")
