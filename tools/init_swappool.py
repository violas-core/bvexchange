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
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from enum import Enum
from baseobject import baseobject
from vlsopt.violasclient import violasclient, violaswallet
import stmanage
import redis
import comm_funs
#module name
name="initworkenv"
wallet_name="vwallet"
VIOLAS_ADDRESS_LEN = comm.values.VIOLAS_ADDRESS_LEN
logger = log.logger.getLogger(name)
def get_amount_out(token_a, token_b, amount_in):
    swap_rate = {"VLSUSD":1.0, "USD":1.0, "VLSGBP":1.2988, "EUR":1.1754, "VLSEUR":1.1754, "VLSSGD": 0.7271, "BTC":10000.0}
    token_a_rate = swap_rate.get(token_a)
    assert token_a_rate is not None, f"not found token({token_a})"

    token_b_rate = swap_rate.get(token_b)
    assert token_b_rate is not None, f"not found token({token_b})"

    print(f"token_a_rate:{token_a_rate} token_b_rate:{token_b_rate}")
    return int(amount_in * (token_a_rate/token_b_rate))

def reg_run():
    logger.debug("***************************************init workenv start*****************************")
    vclient = comm_funs.violasreg(name, stmanage.get_violas_nodes())
    wclient = comm_funs.walletreg(name, wallet_name)

    violas_token_id_list = stmanage.get_support_token_id("violas")
    libra_token_id_list = stmanage.get_support_token_id("libra")
    btc_token_id = "BTC"

    #get support opt-type list id for chain
    opt_list = stmanage.get_type_stable_token()
    l2v_opt_list = [opt for opt in opt_list.keys() if opt.startswith("l2v")]
    v2l_opt_list = [opt for opt in opt_list.keys() if opt.startswith("v2l")]

    #get swap module
    swap_module_address = stmanage.get_swap_module()
    swap_owner_address = swap_module_address
    if swap_module_address == "00000000000000000000000000000001":
        swap_owner_address = "0000000000000000000000000a550c18"
    logger.debug(f"swap pool moudule address({swap_module_address}, owner address{swap_owner_address})")

    init_address(vclient, wclient, swap_owner_address)
    #init swap contract
    ##create swap 
    ret = vclient.swap_set_module_address(swap_module_address)
    assert ret.state == error.SUCCEED

    ret = vclient.swap_set_owner_address(swap_owner_address)
    assert ret.state == error.SUCCEED

    print(vclient.swap_is_swap_address(swap_owner_address).to_json())

    if vclient.get_associate_address() == swap_owner_address:
        module_account = vclient.get_associate_account()
    else:
        ret = wclient.get_account(swap_owner_address)
        assert ret.state == error.SUCCEED, f"account({swap_owner_address}) is not found."
        module_account = ret.datas

    init_address(vclient, wclient, swap_owner_address)

    gas_token_id = violas_token_id_list[0]

    if not vclient.swap_is_swap_address(swap_owner_address).datas: #and vclient.get_associate_address() != swap_owner_address:
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
            in_amount = 1000000_000000
            out_amount = get_amount_out(token_a, token_b, in_amount)
            logger.debug(f"append swap liquidity({token_a} - {token_b}, {in_amount} {out_amount}")
            ret = vclient.swap_add_liquidity(account_l, token_a, token_b, in_amount, out_amount, gas_currency_code = gas_token_id)
            assert ret.state == error.SUCCEED


#test use: init client address
def init_address(vclient, wclient, address):
    violas_token_id_list = stmanage.get_support_token_id("violas")
    libra_token_id_list = stmanage.get_support_token_id("libra")
    btc_token_id = "BTC"

    for token_id in violas_token_id_list:
        comm_funs.init_address_list(vclient, wclient, [address], token_id, minamount = 100000000_000000)


if __name__ == "__main__":
    stmanage.set_conf_env("../bvexchange.toml")
    print(get_amount_out("BTC", "VLSUSD", 1000000))
    print(get_amount_out("BTC", "VLSEUR", 1000000))
    print(get_amount_out("VLSUSD", "BTC", 1000000))
    if len(sys.argv) == 1:
        reg_run()
    elif len(sys.argv) == 2:
        vclient = comm_funs.violasreg(name, stmanage.get_violas_nodes())
        wclient = comm_funs.walletreg(name, wallet_name)
        init_address(vclient, wclient, sys.argv[1])
    else:
        raise Exception(f"argument is None or address(violas)")
