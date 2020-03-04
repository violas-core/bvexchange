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
from vlsopt.violasproof import violasproof
from analysis.analysis_filter import afilter
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

def _test_send_tran_exg(vclient, wclient, ttype, dtype, sender, receiver, module, toaddress, amount = 10):
    aclient = afilter(name, ttype=ttype, dtype=dtype)
    #test v2l
    tran_data = vclient.create_data_for_start(ttype, dtype, receiver)
    ret = wclient.get_account(sender)
    assert ret.state == error.SUCCEED, f"get {sender}'s account failed."
    account = ret.datas

    if module is None:
        vclient.send_platform_coin(account, receiver, amount, tran_data)
    else:
        vclient.send_violas_coin(account, receiver, amount, module, tran_data)

    ret = vclient.get_address_version(account.address.hex())
    version = ret.datas
    ret = vclient.get_transactions(version)
    assert ret.state == error.SUCCEED, f"get transaction={version} failed."
    for data in ret.datas:
        tran_data = aclient.get_tran_data(data)
        if aclient.is_target_tran(tran_data) == False:
            raise Exception(f"{dtype} transaction data's format is invalid.{tran_data}")

        tran_parse = aclient.parse_tran(tran_data)
        logger.info(f"{dtype} start tran is ok.{tran_parse}")

def _get_platform_coin(client, receiver, amount = 1000):
    ret = stmanage.get_sender_address_list("v2l", "libra")
    assert len(ret) > 0, "get senders from setting failed."
    sender = ret[0]
    wclient = violaswallet(name, "vwallet")
    ret = wclient.get_account(sender)
    assert ret.state == error.SUCCEED, "get ({sender}'s account failed.{ret.message})"

    ret = client.send_platform_coin(ret.datas, receiver, amount, data="test_violas")
    assert ret.state == error.SUCCEED, f"send platform coin failed(sender={sender} receiver={receiver} amount = {amount}).{ret.message})"

def run():
    try:
        vclient = comm_funs.violasreg(name, stmanage.get_violas_nodes())
        lclient = comm_funs.violasreg(name, stmanage.get_libra_nodes())
        wclient = comm_funs.walletreg(name, wallet_name)

        #init address and module
        addr_list = []
        laddr_list = []

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
        senders_vbtc = new_account_for_address_list(wclient)
        assert senders_vbtc is not None and len(senders_vbtc) > 0, f"v2b senders[{senders_vbtc}] not found."
        comm_funs.init_address_list(vclient, wclient, senders_vbtc, vbtc_module)
        logger.debug("init b2v senders ok")
        addr_list.extend(senders_vbtc)

        #vlibra sender bind module
        senders_vlibra = new_account_for_address_list(wclient)
        assert senders_vlibra is not None and len(senders_vlibra) > 0, f"v2l senders not found."
        comm_funs.init_address_list(vclient, wclient, senders_vlibra, vlibra_module)
        logger.debug("init l2v senders ok")
        addr_list.extend(senders_vlibra)

        comm_funs.init_address_list(vclient, wclient, senders_vlibra, vlibra_module)

        logger.debug("start bind dtype = v2l chain = violas receiver")
        receivers_v2l = new_account_for_address_list(wclient)
        assert receivers_v2l is not None and len(receivers_v2l) > 0, f"v2l receiver not found."
        comm_funs.address_list_bind_module(vclient, wclient, receivers_v2l, vlibra_module)
        addr_list.extend(receivers_v2l)

        logger.debug("start bind dtype = v2b chain = violas receiver")
        receivers_v2b = new_account_for_address_list(wclient)
        assert receivers_v2b is not None and len(receivers_v2b) > 0, f"v2b receiver not found."
        comm_funs.address_list_bind_module(vclient, wclient, receivers_v2b, vbtc_module)
        addr_list.extend(receivers_v2b)

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

        receivers_l2v = new_account_for_address_list(wclient)
        assert combin is not None and len(combin) > 0, f"v2b combin not found or is invalid."
        laddr_list.extend(receivers_l2v)

        addresses_libra = new_account_for_address_list(wclient)
        assert addresses_libra is not None and len(addresses_libra) > 0, f"libra addresses not found or is invalid."
        _get_platform_coin(lclient, addresses_libra[0])
        laddr_list.extend(addresses_libra)

        addresses_violas = new_account_for_address_list(wclient)
        assert addresses_violas is not None and len(addresses_violas) > 0, f"violas address not found or is invalid."
        comm_funs.init_address_list(vclient, wclient, addresses_violas, vlibra_module)
        addr_list.extend(addresses_violas)


        #v2l 
        _test_send_tran_exg(vclient, wclient, "violas", "v2l", addresses_violas[0], receivers_v2l[0], vlibra_module, addresses_libra[0])
        
        #test l2v
        _test_send_tran_exg(lclient, wclient, "libra", "l2v", addresses_libra[0], receivers_l2v[0], None, addresses_violas[0])

        infos = {}
        print(addr_list)
        comm_funs.list_address_info(vclient, wclient, addr_list, ret = infos)
        json_print(infos)

        linfos = {}
        print(laddr_list)
        comm_funs.list_address_info(lclient, wclient, laddr_list, ret = linfos)
        json_print(linfos)
    except Exception as e:
        parse_except(e)
    finally:
        if wclient is not None:
            wclient.dump_wallet()
if __name__ == "__main__":
    run()
