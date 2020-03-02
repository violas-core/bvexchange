#!/usr/bin/python3
import operator
import sys
import json
import os
sys.path.append(os.getcwd())
sys.path.append("..")
import time
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
import tools.comm_funs as comm_funs
#module name
name="testviolas"
wallet_name= "wallet" + time.strftime("%Y%m%d_%H%M%S", time.localtime()) + ".wlt"

logger = log.logger.getLogger(name)
def new_account_for_address(wclient):
    ret = wclient.new_account()
    assert ret.state == error.SUCCEED, f"new account failed.[ret.datas]"
    logger.info("new account:{ret.datas.address.hex()}")
    return ret.datas.address.hex()

def new_account_for_address_list(wclient, count = 1):
    addrs = []
    for idx in range(count):
        addrs.append(new_account_for_address(wclient))
    return addrs

def run():
    try:
        vclient = comm_funs.violasreg(name, stmanage.get_violas_nodes())
        wclient = comm_funs.walletreg(name, wallet_name)

        infos = {}
        addr_list = []
        #create vbtc module
        vbtc_module = new_account_for_address(wclient)
        assert vbtc_module is not None and len(vbtc_module) == 64, f"vbtc address[{vbtc_module}] is not found"

        if comm_funs.is_module_address(vclient, vbtc_module) == False:
            comm_funs.create_token(vclient, wclient, vbtc_module)
            logger.debug("create vbtc ok")
        else:
            logger.debug("vbtc is exists")

        #create vlibra module
        vlibra_module = new_account_for_address(wclient)
        assert vbtc_module is not None and len(vbtc_module) == 64, "vlibra module is not found"

        if comm_funs.is_module_address(vclient, vlibra_module) == False:
            comm_funs.create_token(vclient, wclient, vlibra_module)
            logger.debug("create vlibra ok")
        else:
            logger.debug("vlibra is exists")

        addr_list.extend([vbtc_module])
        addr_list.extend([vlibra_module])

        #vbtc sender bind  module
        senders = new_account_for_address_list(wclient)
        assert senders is not None and len(senders) > 0, f"v2b senders[{senders}] not found."
        comm_funs.init_address_list(vclient, wclient, senders, vbtc_module)
        logger.debug("init b2v senders ok")
        addr_list.extend(senders)

        #vlibra sender bind module
        senders = new_account_for_address_list(wclient)
        assert senders is not None and len(senders) > 0, f"v2l senders not found."
        logger.debug("init l2v senders ok")
        addr_list.extend(senders)

        comm_funs.init_address_list(vclient, wclient, senders, vlibra_module)

        logger.debug("start bind dtype = v2l chain = violas receiver")
        receivers = new_account_for_address_list(wclient)
        assert receivers is not None and len(receivers) > 0, f"v2l receiver not found."
        comm_funs.address_list_bind_module(vclient, wclient, receivers, vlibra_module)
        addr_list.extend(receivers)

        logger.debug("start bind dtype = v2b chain = violas receiver")
        receivers = new_account_for_address_list(wclient)
        assert receivers is not None and len(receivers) > 0, f"v2b receiver not found."
        comm_funs.address_list_bind_module(vclient, wclient, receivers, vbtc_module)
        addr_list.extend(receivers)

        logger.debug("start bind dtype = v2b chain = violas combin")
        combin = new_account_for_address_list(wclient)
        assert combin is not None and len(combin) > 0, f"v2b combin not found or is invalid."
        comm_funs.address_list_bind_module(vclient, wclient, combin, vbtc_module)
        addr_list.extend(combin)

        logger.debug("start bind dtype = v2l chain = violas combin")
        combin = new_account_for_address_list(wclient)
        assert combin is not None and len(combin) > 0, f"v2l combin not found or is invalid."
        comm_funs.address_list_bind_module(vclient, wclient, combin, vlibra_module)

        addr_list.extend(combin)

        print(addr_list)
        comm_funs.list_address_info(vclient, wclient, addr_list, ret = infos)

        json_print(infos)
    except Exception as e:
        parse_except(e)
    finally:
        if wclient is not None:
            wclient.dump_wallet()
if __name__ == "__main__":
    run()
