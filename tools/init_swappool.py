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
import stmanage
import redis
import comm_funs
#module name
name="initworkenv"
wallet_name="vwallet"
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
    swap_module_address = stmanage.get_swap_module()
    logger.debug(f"swap pool moudule address({swap_module_address})")

    #init swap contract




#test use: init client address
def init_address(address):
    vclient = comm_funs.violasreg(name, stmanage.get_violas_nodes())
    wclient = comm_funs.walletreg(name, wallet_name)
    violas_token_id_list = stmanage.get_support_token_id("violas")
    libra_token_id_list = stmanage.get_support_token_id("libra")
    btc_token_id = "BTCBTC"

    for token_id in violas_token_id_list:
        comm_funs.init_address_list(vclient, wclient, [address], token_id, minamount = 100_000000)

if __name__ == "__main__":
    stmanage.set_conf_env("../bvexchange.toml")
    if len(sys.argv) == 1:
        reg_run()
    elif len(sys.argv) == 2:
        init_address(sys.argv[1])
    else:
        raise Exception(f"argument is None or address(violas)")
