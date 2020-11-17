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
def reg_run():
    logger.debug("***************************************init workenv start*****************************")
    vclient = comm_funs.violasreg(name, stmanage.get_violas_nodes())
    wclient = comm_funs.walletreg(name, wallet_name)

    violas_token_id_list = stmanage.get_support_token_id("violas")
    libra_token_id_list = stmanage.get_support_token_id("libra")

    #get support opt-type list id for chain
    opt_list = stmanage.get_support_mods_info()

    print(f"all token id: {violas_token_id_list}")
    for opt_type in opt_list:
        logger.debug("start bind dtype = {opt_type} chain = violas receiver")
        senders = stmanage.get_sender_address_list(opt_type, "violas")
        receiver = stmanage.get_receiver_address_list(opt_type, "violas")
        combine = stmanage.get_combine_address_list(opt_type, "violas")
        addresses = []
        if senders :
            addresses.extend(senders)
        if receiver:
            addresses.extend(receiver)
        if combine:
            addresses.extend(combine)
        for token_id in violas_token_id_list:
            if len(addresses) > 0:
                comm_funs.init_address_list(vclient, wclient, addresses, token_id, minamount = 1000_000000)
    #vlibra sender bind token_id
    #logger.debug("***************************************init vlibra sender*****************************")
    #for opt_type in l2v_opt_list:
    #    senders = stmanage.get_sender_address_list(opt_type, "violas")
    #    assert senders is not None and len(senders) > 0, f"{opt_type} senders not found."
    #    #comm_funs.init_address_list(vclient, wclient, senders, opt_list.get(opt_type))
    #    for token_id in violas_token_id_list:
    #        comm_funs.init_address_list(vclient, wclient, senders, token_id, minamount = 100_000000)
    #logger.debug("init l2v senders ok")

    #logger.debug("***************************************bind module: v2l receiver*****************************")
    #for opt_type in v2l_opt_list:
    #    logger.debug("start bind dtype = {opt_type} chain = violas receiver")
    #    receivers = stmanage.get_receiver_address_list(opt_type, "violas")
    #    assert receivers is not None and len(receivers) > 0, f"{opt_type} receiver not found."
    #    for token_id in violas_token_id_list:
    #        comm_funs.init_address_list(vclient, wclient, receivers, token_id, minamount = 100_000000)


#test use: init client address
def init_address(address):
    vclient = comm_funs.violasreg(name, stmanage.get_violas_nodes())
    wclient = comm_funs.walletreg(name, wallet_name)
    violas_token_id_list = stmanage.get_support_token_id("violas")
    libra_token_id_list = stmanage.get_support_token_id("libra")
    btc_token_id = "BTC"

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
