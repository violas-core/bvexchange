#!/usr/bin/python3
import operator
import sys
import json
import os
import time
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
from tools import comm_funs
from comm.result import result, parse_except
from comm.error import error
from db.dbb2v import dbb2v
from enum import Enum
from baseobject import baseobject
from vlsopt.violasclient import violasclient, violaswallet
import stmanage
import redis
#module name
name="initworkenv"
#wallet_name= "wallet" + time.strftime("%Y%m%d_%H%M%S", time.localtime()) + ".wlt"
wallet_name= "vwallet"
VIOLAS_ADDRESS_LEN = comm.values.VIOLAS_ADDRESS_LEN
logger = log.logger.getLogger(name)
def reg_run():
    logger.debug("***************************************init workenv start*****************************")
    vclient = comm_funs.violasreg(name, stmanage.get_violas_nodes())
    wclient = comm_funs.walletreg(name, wallet_name)

    violas_token_id_list = stmanage.get_support_token_id("violas")
    libra_token_id_list = stmanage.get_support_token_id("libra")
    btc_token_id = "BTCBTC"

    #get support opt-type list id for chain
    opt_list = stmanage.get_type_stable_token()
    l2v_opt_list = [opt for opt in opt_list.keys() if opt.startswith("l2v")]
    v2l_opt_list = [opt for opt in opt_list.keys() if opt.startswith("v2l")]

    #get swap module
    #account_module = wclient.new_account().datas
    #swap_module_address = account_module.auth_key_prefix.hex() + account_module.address.hex()
    swap_module_address = stmanage.get_swap_module()
    logger.debug(f"swap pool moudule address({swap_module_address})")

    init_address(vclient, wclient, swap_module_address)
    #init swap contract
    ##create swap 
    ret = vclient.swap_set_module_address(swap_module_address)
    assert ret.state == error.SUCCEED

    ret = wclient.get_account(swap_module_address)
    assert ret.state == error.SUCCEED, f"account({swap_module_address}) is not found."

    module_account = ret.datas

    init_address(vclient, wclient, module_account.address.hex())

    gas_token_id = violas_token_id_list[0]

    #receive swap token
    receiver_address = "eda54651162270ccc0ff81cbcfffcded8ee2a1a52bd868c0baadb0d226731832"
    init_address(vclient, wclient, receiver_address)

    if not vclient.swap_is_swap_address(module_account.address.hex()).datas:
        logger.debug(f"init swap contract({module_account.address.hex()})")
        ret = vclient.swap_publish_contract(module_account, gas_currency_code = gas_token_id)
        assert ret.state == error.SUCCEED

        ret = vclient.swap_initialize(module_account, gas_currency_code = gas_token_id)
        assert ret.state == error.SUCCEED

    ret = vclient.swap_get_registered_tokens()
    assert ret.state == error.SUCCEED
    had_tokens = ret.datas
    for token_a in violas_token_id_list:
        logger.debug(f"append swap token({token_a})")
        if token_a in had_tokens:
            logger.debug(f"token({token_a}) is exists, next..")
            continue
        ret = vclient.swap_add_currency(module_account, token_a, gas_currency_code = gas_token_id)
        assert ret.state == error.SUCCEED

    account_l = wclient.new_account().datas
    addr_l = account_l.auth_key_prefix.hex() + account_l.address.hex()
    init_address(vclient, wclient, addr_l)

    for token_a in violas_token_id_list:
        for token_b in violas_token_id_list:
            if token_a == token_b:
                continue
            logger.debug(f"append swap liquidity({token_a} - {token_b})")
            ret = vclient.swap_add_liquidity(account_l, token_a, token_b, 1_000000, 1_000000, gas_currency_code = gas_token_id)
            assert ret.state == error.SUCCEED

    
    #swap 
    account_s = wclient.new_account().datas
    addr_s = account_s.auth_key_prefix.hex() + account_s.address.hex()
    init_address(vclient, wclient, addr_s)
    swap_info = []
    logger.debug(f"swap address :{addr_s}")
    for token_a in violas_token_id_list:
        for token_b in violas_token_id_list:
            if token_a == token_b:
                continue
            logger.debug(f"swap start:{token_a}/{token_b}")
            swap_amount = 1_000000

            ret = vclient.swap_get_output_amount(token_a, token_b, swap_amount)
            assert ret.state == error.SUCCEED
            amount_out, gas = ret.datas
            logger.debug(f"swap amount out:{token_a}/{token_b} value = {amount_out}, gas = {gas}")

            ret = vclient.get_balance(addr_s, token_a)
            assert ret.state == error.SUCCEED
            amount_before_a = ret.datas

            ret = vclient.get_balance(addr_s, token_b)
            assert ret.state == error.SUCCEED
            amount_before_b = ret.datas

            logger.debug(f"will exec swap")
            ret = vclient.get_balance(receiver_address, token_b)
            assert ret.state == error.SUCCEED
            receiver_amount_before_b = ret.datas

            ret = vclient.swap(account_s, token_a, token_b, swap_amount, amount_out, receiver = receiver_address, gas_currency_code = gas_token_id)
            assert ret.state == error.SUCCEED

            ret = vclient.get_balance(receiver_address, token_b)
            assert ret.state == error.SUCCEED
            receiver_amount_after_b = ret.datas

            logger.debug(f"exec swap end")
            ret = vclient.get_balance(addr_s, token_a)
            assert ret.state == error.SUCCEED
            amount_after_a = ret.datas

            ret = vclient.get_balance(addr_s, token_b)
            assert ret.state == error.SUCCEED
            amount_after_b = ret.datas

            check_avg = amount_before_a == amount_after_a + gas
            diff_b = amount_after_b - amount_before_b
            diff_a = amount_after_a - amount_before_a
            swap_info.append({"receiver_amount_before_b": receiver_amount_before_b, "receiver_amount_after_b": receiver_amount_after_b, "receiver_change": receiver_amount_after_b - receiver_amount_before_b, "amount_out": amount_out, "before_a": amount_before_a, "before_b" : amount_before_b, "after_a": amount_after_a, "after_b": amount_after_b, "a/b":token_a + "/" + token_b, "gas":gas, "diff_a": diff_a, "diff_b":diff_b})
    
    for info in swap_info:
        print(info)


#test use: init client address
def init_address(vclient, wclient, address):
    violas_token_id_list = stmanage.get_support_token_id("violas")
    libra_token_id_list = stmanage.get_support_token_id("libra")
    btc_token_id = "BTCBTC"

    for token_id in violas_token_id_list:
        comm_funs.init_address_list(vclient, wclient, [address], token_id, minamount = 1000_000000)

def init_stmanage():
    stmanage.set_conf_env("../bvexchange.toml")

if __name__ == "__main__":
    init_signal()
    pa = parseargs(globals())
    pa.test(sys.argv)
