#!/usr/bin/python3
import operator
import sys, getopt
import json
import os
sys.path.append(os.getcwd())
sys.path.append("..")
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
import log
import log.logger
import traceback
import datetime
import stmanage
import requests
import comm
import comm.error
import comm.result
from comm.result import result
from comm.error import error
from comm.parseargs import parseargs
from comm.functions import json_print
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from btc.btcclient import btcclient
from btc.btcwallet import btcwallet
from dataproof import dataproof
from enum import Enum

#module name
name="btctools"

#load logging
logger = log.logger.getLogger(name) 

def getbtcclient():
    return btcclient(name, stmanage.get_btc_conn())

def getbtcwallet():
    return btcwallet(name, dataproof.wallets("btc"))

def getb2vtransaction(cursor, limit = 1):
    client = getbtcclient()
    ret = client.get_transactions(cursor, limit)
    assert ret.state == error.SUCCEED, " getb2vtransaction failed"
    for data in ret.datas:
        print(data.to_json())

def showaccountlist():
    bwallet = getbtcwallet() 
    json_print(bwallet.wallet_info)

def gettransaction(tranid):
    client = getbtcclient()
    ret = client.get_tran_by_tranid(tranid)
    assert ret.state == error.SUCCEED, " gettransaction failed"
    print(ret.to_json())

def sendtoaddress(address, amount):
    client = getbtcclient()
    ret = client.sendtoaddress(address, amount)
    assert ret.state == error.SUCCEED, " sendtoaddress failed"
    print(ret.datas)
    
def sendexproofstart(opttype, fromaddress, toaddress, amount, vaddress, sequence, vtoken):
    client = getbtcclient()
    ret = client.sendexproofstart(opttype, fromaddress, toaddress, amount, vaddress, sequence, vtoken)
    assert ret.state == error.SUCCEED, " sendexproofstart failed"
    print(ret.datas)

def sendexproofend(fromaddress, toaddress, vaddress, sequence, vamount, version):
    client = getbtcclient()
    ret = client.sendexproofend(fromaddress, toaddress, vaddress, sequence, vamount, version)
    assert ret.state == error.SUCCEED, " sendexproofend failed"
    print(ret.datas)

def sendexproofmark(fromaddress, toaddress, toamount, vaddress, sequence, version):
    client = getbtcclient()
    ret = client.sendexproofmark(fromaddress, toaddress, toamount, vaddress, sequence, version)
    assert ret.state == error.SUCCEED, "sendexproofmark failed"
    print(ret.datas)

def generatetoaddress(count, address):
    client = getbtcclient()
    ret = client.generatetoaddress(count, address)
    assert ret.state == error.SUCCEED, " generatetoaddress failed"
    print(ret.datas)
    
def listunspent(minconf = 1, maxconf = 9999999, addresses = None, include_unsafe = True, query_options = None):
    client = getbtcclient()
    ret = client.listunspent(minconf, maxconf, addresses, include_unsafe, query_options)
    assert ret.state == error.SUCCEED, " listunspent failed"
    for data in ret.datas:
        print("address:{}, amount:{}".format(data["address"], data["amount"]))

def listexproofforstart(opttype, receiver, excluded = None):
    client = getbtcclient()
    ret = client.listexproofforstart(opttype, receiver, excluded)
    assert ret.state == error.SUCCEED, " listexproofforstart failed"
    print(ret.datas)

def listexproofforend(opttype, receiver, excluded = None):
    client = getbtcclient()
    ret = client.listexproofforend(opttype, receiver, excluded)
    assert ret.state == error.SUCCEED, " listexproofforend failed"
    print(ret.datas)

def listexproofforstop(opttype, receiver, excluded = None):
    client = getbtcclient()
    ret = client.listexproofforstop(opttype, receiver, excluded)
    assert ret.state == error.SUCCEED, " listexproofforstop failed"
    print(ret.datas)

def listexproofformark(receiver, excluded = None):
    client = getbtcclient()
    ret = client.listexproofformark(receiver, excluded)
    assert ret.state == error.SUCCEED, " listexproofformark failed"
    print(ret.datas)

def listexproofforb2v(cursor, limit = 10):
    client = getbtcclient()
    ret = client.listexproofforb2v(cursor, limit)
    assert ret.state == error.SUCCEED, " listexproofforb2v failed"
    print(ret.datas)

def btchelp():
    client = getbtcclient()
    ret = client.help()
    assert ret.state == error.SUCCEED, " btchelp failed"
    print(ret.datas)

def getwalletbalance():
    client = getbtcclient()
    ret = client.getwalletbalance()
    assert ret.state == error.SUCCEED, "getwalletbalance failed"
    print(f"wallet balance:{ret.datas:.8f}")

def getwalletaddressbalance(address):
    client = getbtcclient()
    ret = client.getwalletaddressbalance(address)

    json_print(ret.to_json())

def getrawtransaction(txid, verbose = True):
    client = getbtcclient()
    ret = client.call_original_cli("getrawtransaction", txid, verbose)

    json_print(ret.to_json())


def init_args(pargs):
    pargs.append("help", "show arg list")
    pargs.append("conf", "config file path name. default:bvexchange.toml, find from . and /etc/bvexchange/", True, "toml file", priority = 10)
    pargs.append("wallet", "inpurt wallet file or mnemonic, input is btc wallet file or pairs(ADDRESS:PRIVKEY, ADDRESS:PRIVKEY)", True, "file name/pairs", priority = 13, argtype = parseargs.argtype.STR)

    pargs.append(sendexproofstart,f"create new exchange start proof. opttype: {[opttype for opttype in stmanage.get_support_dtypes() if opttype.startswith('b2')]}")
    pargs.append(sendexproofend, "create new exchange end proof.")
    pargs.append(sendexproofmark, "create new exchange mark proof, subtract fee from toamount.")
    pargs.append(generatetoaddress, "generate new block to address.")
    pargs.append(listunspent, "returns array of unspent transaction outputs.")
    pargs.append(listexproofforstart, "returns array of proof state is start .")
    pargs.append(listexproofforend, "returns array of proof state is end .")
    pargs.append(listexproofforstop, "returns array of proof state is stop.")
    pargs.append(listexproofformark, "returns array of proof state is mark .")
    pargs.append(listexproofforb2v, "returns array of proof list type = b2v.")
    pargs.append(btchelp, "returns bitcoin-cli help.")
    pargs.append(getwalletbalance, "returns wallet balance.")
    pargs.append(getwalletaddressbalance, "returns wallet target address's balance.")
    pargs.append(getb2vtransaction, "returns array of proof list.[map to violas format]")
    pargs.append(gettransaction, "returns proof info.")
    pargs.append(getrawtransaction, "returns raw transaction info.")
    pargs.append(showaccountlist, "returns account info.")

def run(argc, argv):
    try:
        logger.debug("start btc.main")
        if stmanage.get_conf_env() is None:
            stmanage.set_conf_env("bvexchange.toml") 
        pargs = parseargs()
        init_args(pargs)
        pargs.show_help(argv)
        opts, err_args = pargs.getopt(argv)
    except getopt.GetoptError as e:
        logger.error(e)
        sys.exit(2)
    except Exception as e:
        logger.error(e)
        sys.exit(2)

    #argument start for --
    if len(err_args) > 0:
        pargs.show_args()

    names = [opt for opt, arg in opts]
    pargs.check_unique(names)

    #--conf must be first
    if stmanage.get_conf_env() is None:
        stmanage.set_conf_env_default() 

    for opt, arg in opts:
        count, arg_list = pargs.split_arg(opt, arg)
        print("opt = {}, arg = {}".format(opt, arg_list))
        if pargs.is_matched(opt, ["conf"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            stmanage.set_conf_env(arg_list[0])
        elif pargs.is_matched(opt, ["wallet"]):
            pargs.exit_check_opt_arg(opt, arg, 1)
            dataproof.wallets.update_wallet("btc", arg_list[0])
        elif pargs.has_callback(opt):
            pargs.callback(opt, *arg_list)
        else:
            raise Exception(f"not found matched opt{opt}")
    logger.debug("end manage.main")

if __name__ == "__main__":
    run(len(sys.argv) - 1, sys.argv[1:])
