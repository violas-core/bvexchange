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

    opt_list = stmanage.get_type_token_map()
    l2v_opt_list = [opt for opt in opt_list.keys() if opt.startswith("l2v")]
    v2l_opt_list = [opt for opt in opt_list.keys() if opt.startswith("v2l")]

    #logger.debug("***************************************init vbtc sender*****************************")
    ##vbtc sender bind  token_id
    #senders = stmanage.get_sender_address_list("b2v", "violas")
    #assert senders is not None and len(senders) > 0, f"v2b senders[{senders}] not found."
    #comm_funs.address_list_bind_token_id(vclient, wclient, senders, )
    #comm_funs.init_address_list(vclient, wclient, senders, vbtc_token_address, btc_token_id)
    #logger.debug("init b2v senders ok")

    #vlibra sender bind token_id
    logger.debug("***************************************init vlibra sender*****************************")
    for opt_type in l2v_opt_list:
        senders = stmanage.get_sender_address_list(opt_type, "violas")
        assert senders is not None and len(senders) > 0, f"{opt_type} senders not found."
        comm_funs.init_address_list(vclient, wclient, senders, opt_list.get(opt_type))
    logger.debug("init l2v senders ok")

    logger.debug("***************************************bind module: v2l receiver*****************************")
    for opt_type in v2l_opt_list:
        logger.debug("start bind dtype = {opt_type} chain = violas receiver")
        receivers = stmanage.get_receiver_address_list(opt_type, "violas")
        assert receivers is not None and len(receivers) > 0, f"{opt_type} receiver not found."
        for token_id in violas_token_id_list:
            comm_funs.init_address_list(vclient, wclient, receivers, token_id, minamount = 1_000000)

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
