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
import comm_funs
#module name
name="initworkenv"
wallet_name="vwallet"

logger = log.logger.getLogger(name)
def reg_run():
    vclient = comm_funs.violasreg(name, stmanage.get_violas_nodes())
    wclient = comm_funs.walletreg(name, wallet_name)

    #create vbtc module
    vbtc_module = stmanage.get_module_address("v2b", "violas")
    assert vbtc_module is not None and len(vbtc_module) == 64, f"vbtc address[{vbtc_module}] is not found"

    if comm_funs.is_module_address(vclient, vbtc_module) == False:
        comm_funs.create_token(vclient, wclient, vbtc_module)
        logger.debug("create vbtc ok")
    else:
        logger.debug("vbtc is exists")


    #create vlibra module
    vlibra_module = stmanage.get_module_address("v2l", "violas")
    assert vbtc_module is not None and len(vbtc_module) == 64, "vlibra module is not found"

    if comm_funs.is_module_address(vclient, vlibra_module) == False:
        comm_funs.create_token(vclient, wclient, vlibra_module)
        logger.debug("create vlibra ok")
    else:
        logger.debug("vlibra is exists")


    #vbtc sender bind  module
    senders = stmanage.get_sender_address_list("b2v", "violas")
    assert senders is not None and len(senders) > 0, f"v2b senders[{senders}] not found."
    comm_funs.init_address_list(vclient, wclient, senders, vbtc_module)
    logger.debug("init b2v senders ok")

    #vlibra sender bind module
    senders = stmanage.get_sender_address_list("l2v", "violas")
    assert senders is not None and len(senders) > 0, f"v2l senders not found."
    logger.debug("init l2v senders ok")

    comm_funs.init_address_list(vclient, wclient, senders, vlibra_module)

    logger.debug("start bind dtype = v2l chain = violas receiver")
    receivers = stmanage.get_receiver_address_list("v2l", "violas")
    assert receivers is not None and len(receivers) > 0, f"v2l receiver not found."
    comm_funs.address_list_bind_module(vclient, wclient, receivers, vlibra_module)

    logger.debug("start bind dtype = v2b chain = violas receiver")
    receivers = stmanage.get_receiver_address_list("v2b", "violas")
    assert receivers is not None and len(receivers) > 0, f"v2b receiver not found."
    comm_funs.address_list_bind_module(vclient, wclient, receivers, vbtc_module)

    logger.debug("start bind dtype = v2b chain = violas combin")
    combin = stmanage.get_combine_address("v2b", "violas")
    assert combin is not None and len(combin) > 0, f"v2b combin not found or is invalid."
    comm_funs.address_list_bind_module(vclient, wclient, [combin], vbtc_module)

    logger.debug("start bind dtype = v2l chain = violas combin")
    combin = stmanage.get_combine_address("v2l", "violas")
    assert combin is not None and len(combin) == 64, f"v2l combin not found or is invalid."
    comm_funs.address_list_bind_module(vclient, wclient, [combin], vlibra_module)
if __name__ == "__main__":
    reg_run()
