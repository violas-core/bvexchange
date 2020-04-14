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
import comm.values
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

VIOLAS_ADDRESS_LEN = comm.values.VIOLAS_ADDRESS_LEN
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
        logger.debug("****create module\n")
        module = new_account_for_address(wclient)
        assert module is not None and len(module) in VIOLAS_ADDRESS_LEN , f"module address[{module}] is not found"
        comm_funs.publish_module(vclient, wclient, module)

        #create vbtc module
        logger.debug("\n\n****start create vbtc\n")
        vbtc_module = new_account_for_address(wclient)
        assert vbtc_module is not None and len(vbtc_module) in VIOLAS_ADDRESS_LEN, f"vbtc address[{vbtc_module}] is not found"

        (seq, vbtc_id) = comm_funs.create_token(vclient, wclient, vbtc_module, module)
        logger.debug(f"****create vbtc ok. seq = {seq} btc_id = {vbtc_id}\n")

        #create vlibra module
        logger.debug("\n\n****start create vlibra\n")
        vlibra_module = new_account_for_address(wclient)
        assert vbtc_module is not None and len(vbtc_module) in VIOLAS_ADDRESS_LEN, "vlibra module is not found"

        (seq, vlibra_id) = comm_funs.create_token(vclient, wclient, vlibra_module, module)
        logger.debug("****create vlibra ok seq = {seq} vlibra_id = {vlibra_id}\n")

        addr_list.extend([module])
        addr_list.extend([vbtc_module])
        addr_list.extend([vlibra_module])

        #vbtc sender bind  module
        logger.debug("\n\n****start vbtc sender bind module\n")
        senders_vbtc = new_account_for_address_list(wclient)
        assert senders_vbtc is not None and len(senders_vbtc) > 0, f"v2b senders[{senders_vbtc}] not found."
        comm_funs.init_address_list(vclient, wclient, senders_vbtc, vbtc_module, vbtc_id, module)
        logger.debug("****init b2v senders ok")
        addr_list.extend(senders_vbtc)

        #vlibra sender bind module
        logger.debug("\n\n****start vlibra sender bind module\n")
        senders_vlibra = new_account_for_address_list(wclient)
        assert senders_vlibra is not None and len(senders_vlibra) > 0, f"v2l senders not found."
        comm_funs.init_address_list(vclient, wclient, senders_vlibra, vlibra_module, vlibra_id, module)
        logger.debug("\n\n****init l2v senders ok")
        addr_list.extend(senders_vlibra)

        logger.debug("\n\n****start bind dtype = v2l chain = violas receiver\n")
        receivers_v2l = new_account_for_address_list(wclient)
        assert receivers_v2l is not None and len(receivers_v2l) > 0, f"v2l receiver not found."
        comm_funs.address_list_bind_module(vclient, wclient, receivers_v2l, module)
        comm_funs.init_address_list(vclient, wclient, receivers_v2l, vlibra_module, vlibra_id, module)
        addr_list.extend(receivers_v2l)

        logger.debug("\n\n****start bind dtype = v2b chain = violas receiver\n")
        receivers_v2b = new_account_for_address_list(wclient)
        assert receivers_v2b is not None and len(receivers_v2b) > 0, f"v2b receiver not found."
        comm_funs.address_list_bind_module(vclient, wclient, receivers_v2b, module)
        comm_funs.init_address_list(vclient, wclient, receivers_v2b, vbtc_module, vbtc_id, module)
        addr_list.extend(receivers_v2b)

        logger.debug("\n\n****start bind dtype = v2b chain = violas combin\n")
        combin = new_account_for_address_list(wclient)
        assert combin is not None and len(combin) > 0, f"v2b combin not found or is invalid."
        comm_funs.address_list_bind_module(vclient, wclient, combin, module)
        addr_list.extend(combin)

        logger.debug("\n\n****start bind dtype = v2l chain = violas combin\n")
        combin = new_account_for_address_list(wclient)
        assert combin is not None and len(combin) > 0, f"v2l combin not found or is invalid."
        comm_funs.address_list_bind_module(vclient, wclient, combin, module)
        addr_list.extend(combin)

        receivers_l2v = new_account_for_address_list(wclient)
        assert combin is not None and len(combin) > 0, f"v2b combin not found or is invalid."
        laddr_list.extend(receivers_l2v)

        logger.debug("\n\n****get libra address and coin(libra)\n")
        addresses_libra = new_account_for_address_list(wclient)
        assert addresses_libra is not None and len(addresses_libra) > 0, f"libra addresses not found or is invalid."
        _get_platform_coin(lclient, addresses_libra[0])
        laddr_list.extend(addresses_libra)

        addresses_violas = new_account_for_address_list(wclient)
        assert addresses_violas is not None and len(addresses_violas) > 0, f"violas address not found or is invalid."
        comm_funs.init_address_list(vclient, wclient, addresses_violas, module)
        comm_funs.address_list_bind_module(vclient, wclient, addresses_violas, module)
        addr_list.extend(addresses_violas)

        #v2l 
        logger.debug("\n\n****test send tran exg(violas)\n")
        _test_send_tran_exg(vclient, wclient, "violas", "v2l", addresses_violas[0], receivers_v2l[0], vlibra_module, addresses_libra[0])
        
        #test l2v
        logger.debug("\n\n****test send tran exg(libra)\n")
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
