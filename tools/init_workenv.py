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
    vclient = comm_funs.violasreg(name, stmanage.get_violas_nodes())
    wclient = comm_funs.walletreg(name, wallet_name)

    vbtc_token_id = -1
    vlibra_token_id = -1
    vbtc_token_address = None
    vlibra_token_address = None
    logger.debug("***************************************create vbtc*****************************")
    vbtc_name = "vbtci001"
    vbtc_module = stmanage.get_module_address("v2b", "violas")
    vbtc_token_address = stmanage.get_token_address("v2b", "violas")
    assert vbtc_module is not None and len(vbtc_module) in VIOLAS_ADDRESS_LEN, f"vbtc address[{vbtc_module}] is not found"

    if not comm_funs.is_module_address(vclient, vbtc_module):
        comm_funs.publish_module(vclient, wclient, vbtc_module)
        logger.debug("create vbtc ok")
    else:
        logger.debug(f"vbtc module({vbtc_module}) is exists")

    ret = vclient.has_token_name(vbtc_module, vbtc_name)
    assert ret.state == error.SUCCEED, f"check token name({vbtc_name}) failed."

    if not ret.datas:
        _, vbtc_token_id = comm_funs.create_token(vclient, wclient, vbtc_token_address, vbtc_module, vbtc_name)
    else:
        logger.debug(f"vbtc token({vbtc_token_address}) name={vbtc_name} is exists")
        ret = vclient.get_token_id(vbtc_module, vbtc_name)
        assert ret.state == error.SUCCEED, f"get token id faild. module= {vbtc_module}, token name: {vbtc_name}"
        vbtc_token_id = ret.datas

    logger.debug("***************************************create vlibra***************************") 
    vlibra_name = "vlibrai001"
    vlibra_module = stmanage.get_module_address("v2l", "violas")
    vlibra_token_address = stmanage.get_token_address("v2l", "violas")

    assert vlibra_module is not None and len(vlibra_module) in VIOLAS_ADDRESS_LEN, "vlibra module is not found"

    if not comm_funs.is_module_address(vclient, vlibra_module):
        comm_funs.publish_module(vclient, wclient, vlibra_module)
        logger.debug("create vlibra ok")
    else:
        logger.debug(f"vlibra module({vlibra_module}) is exists")

    ret = vclient.has_token_name(vlibra_module, vlibra_name)
    assert ret.state == error.SUCCEED, f"check token name({vlibra_name}) failed."

    if not ret.datas:
        _, vlibra_token_id = comm_funs.create_token(vclient, wclient, vlibra_token_address, vlibra_module, vlibra_name)
    else:
        logger.debug(f"vbtc token{vlibra_token_address} name={vbtc_name} is exists")
        ret = vclient.get_token_id(vlibra_module, vlibra_name)
        assert ret.state == error.SUCCEED, f"get token id faild. module= {vlibra_module}, token name: {vlibra_name}"
        vlibra_token_id = ret.datas

    logger.debug("***************************************init vbtc sender*****************************")
    #vbtc sender bind  module
    senders = stmanage.get_sender_address_list("b2v", "violas")
    assert senders is not None and len(senders) > 0, f"v2b senders[{senders}] not found."
    comm_funs.address_list_bind_module(vclient, wclient, senders, vbtc_module)
    comm_funs.init_address_list(vclient, wclient, senders, vbtc_token_address, vbtc_token_id, vbtc_module)
    logger.debug("init b2v senders ok")

    #vlibra sender bind module
    logger.debug("***************************************init vlibra sender*****************************")
    senders = stmanage.get_sender_address_list("l2v", "violas")
    assert senders is not None and len(senders) > 0, f"v2l senders not found."
    comm_funs.address_list_bind_module(vclient, wclient, senders, vlibra_module)
    comm_funs.init_address_list(vclient, wclient, senders, vlibra_token_address, vlibra_token_id, vlibra_module)
    logger.debug("init l2v senders ok")

    logger.debug("***************************************bind module: v2l receiver*****************************")
    logger.debug("start bind dtype = v2l chain = violas receiver")
    receivers = stmanage.get_receiver_address_list("v2l", "violas")
    assert receivers is not None and len(receivers) > 0, f"v2l receiver not found."
    comm_funs.address_list_bind_module(vclient, wclient, receivers, vlibra_module)

    logger.debug("***************************************bind module: v2b receiver*****************************")
    logger.debug("start bind dtype = v2b chain = violas receiver")
    receivers = stmanage.get_receiver_address_list("v2b", "violas")
    assert receivers is not None and len(receivers) > 0, f"v2b receiver not found."
    comm_funs.address_list_bind_module(vclient, wclient, receivers, vbtc_module)

    logger.debug("***************************************bind module: v2b combin*****************************")
    logger.debug("start bind dtype = v2b chain = violas combin")
    combin = stmanage.get_combine_address("v2b", "violas")
    assert combin is not None and len(combin) in VIOLAS_ADDRESS_LEN, f"v2b combin not found or is invalid."
    comm_funs.address_list_bind_module(vclient, wclient, [combin], vbtc_module)

    logger.debug("***************************************bind module: v2l combin*****************************")
    logger.debug("start bind dtype = v2l chain = violas combin")
    combin = stmanage.get_combine_address("v2l", "violas")
    assert combin is not None and len(combin) in VIOLAS_ADDRESS_LEN, f"v2l combin not found or is invalid."
    comm_funs.address_list_bind_module(vclient, wclient, [combin], vlibra_module)
if __name__ == "__main__":
    reg_run()
