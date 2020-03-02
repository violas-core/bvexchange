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
from comm.functions import json_print
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
name="showworkenv"
wallet_name="vwallet"

logger = log.logger.getLogger(name)

def run():
    vclient = comm_funs.violasreg(name, stmanage.get_violas_nodes())
    wclient = comm_funs.walletreg(name, wallet_name)

    infos = {}
    #create vbtc module
    module = stmanage.get_module_address("v2b", "violas")
    assert module is not None and len(module) == 64, f"vbtc address[{module}] is not found"

    comm_funs.list_address_info(vclient, wclient, [module], ret = infos)

    #create vlibra module
    module = stmanage.get_module_address("v2l", "violas")
    assert module is not None and len(module) == 64, "vlibra module is not found"

    comm_funs.list_address_info(vclient, wclient, [module], ret = infos)

    #vbtc sender bind  module
    senders = stmanage.get_sender_address_list("b2v", "violas")
    assert senders is not None and len(senders) > 0, f"v2b senders[{senders}] not found."

    comm_funs.list_address_info(vclient, wclient, senders, ret = infos)

    #vlibra sender bind module
    senders = stmanage.get_sender_address_list("l2v", "violas")
    assert senders is not None and len(senders) > 0, f"v2l senders not found."

    comm_funs.list_address_info(vclient, wclient, senders, ret = infos)

    receivers = stmanage.get_receiver_address_list("v2l", "violas")
    assert receivers is not None and len(receivers) > 0, f"v2l receiver not found."

    comm_funs.list_address_info(vclient, wclient, receivers, ret = infos)

    receivers = stmanage.get_receiver_address_list("v2b", "violas")
    assert receivers is not None and len(receivers) > 0, f"v2b receiver not found."
    comm_funs.list_address_info(vclient, wclient, receivers, ret = infos)

    combin = stmanage.get_combine_address("v2b", "violas")
    assert combin is not None and len(combin) > 0, f"v2b combin not found or is invalid."
    comm_funs.list_address_info(vclient, wclient, [combin], ret = infos)

    logger.debug("start bind dtype = v2l chain = violas combin")
    combin = stmanage.get_combine_address("v2l", "violas")
    assert combin is not None and len(combin) == 64, f"v2l combin not found or is invalid."
    comm_funs.list_address_info(vclient, wclient, [combin], ret = infos)

    json_print(infos)
if __name__ == "__main__":
    run()
