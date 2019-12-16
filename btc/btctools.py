#!/usr/bin/python3
import operator
import sys, getopt
import json
import os
sys.path.append("..")
sys.path.append("../packages")
import log
import log.logger
import traceback
import datetime
import setting
import requests
import libra
from libra.json_print import json_print
import comm
import comm.error
import comm.result
from comm.result import result
from comm.error import error
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from btc.btcclient import btcclient
from enum import Enum

#module name
name="btcclient"

#load logging
logger = log.logger.getLogger(name) 

def sendtoaddress(address, amount):
    client = btcclient(setting.traceback_limit, setting.btc_conn)
    ret = client.sendtoaddress(address, amount)
    assert ret.state == error.SUCCEED, " sendtoaddress failed"
    print(ret.datas)
    
def sendexproofstart(fromaddress, toaddress, amount, vaddress, sequence, vtoken):
    client = btcclient(setting.traceback_limit, setting.btc_conn)
    ret = client.sendexproofstart(fromaddress, toaddress, amount, vaddress, sequence, vtoken)
    assert ret.state == error.SUCCEED, " sendexproofstart failed"
    print(ret.datas)

def sendexproofend(fromaddress, toaddress, vaddress, sequence, vamount, version):
    client = btcclient(setting.traceback_limit, setting.btc_conn)
    ret = client.sendexproofend(fromaddress, toaddress, vaddress, sequence, vamount, version)
    assert ret.state == error.SUCCEED, " sendexproofend failed"
    print(ret.datas)

def sendexproofmark(fromaddress, toaddress, toamount, vaddress, sequence, version):
    client = btcclient(setting.traceback_limit, setting.btc_conn)
    ret = client.sendexproofmark(fromaddress, toaddress, toamount, vaddress, sequence, version)
    assert ret.state == error.SUCCEED, "sendexproofmark failed"
    print(ret.datas)

def generatetoaddress(count, address):
    client = btcclient(setting.traceback_limit, setting.btc_conn)
    ret = client.generatetoaddress(count, address)
    assert ret.state == error.SUCCEED, " generatetoaddress failed"
    print(ret.datas)
    
def listunspent(minconf = 1, maxconf = 9999999, addresses = None, include_unsafe = True, query_options = None):
    client = btcclient(setting.traceback_limit, setting.btc_conn)
    ret = client.listunspent(minconf, maxconf, addresses, include_unsafe, query_options)
    assert ret.state == error.SUCCEED, " listunspent failed"
    for data in ret.datas:
        print("address:{}, amount:{}".format(data["address"], data["amount"]))

def listexproofforstart(receiver, excluded = None):
    client = btcclient(setting.traceback_limit, setting.btc_conn)
    ret = client.listexproofforstart(receiver, excluded)
    assert ret.state == error.SUCCEED, " listexproofforstart failed"
    for data in ret.datas:
        print(data)

def listexproofforend(receiver, excluded = None):
    client = btcclient(setting.traceback_limit, setting.btc_conn)
    ret = client.listexproofforend(receiver, excluded)
    assert ret.state == error.SUCCEED, " listexproofforend failed"
    for data in ret.datas:
        print(data)

def listexproofformark(receiver, excluded = None):
    client = btcclient(setting.traceback_limit, setting.btc_conn)
    ret = client.listexproofformark(receiver, excluded)
    assert ret.state == error.SUCCEED, " listexproofformark failed"
    for data in ret.datas:
        print(data)

def btchelp():
    client = btcclient(setting.traceback_limit, setting.btc_conn)
    ret = client.help()
    assert ret.state == error.SUCCEED, " btchelp failed"
    print(ret.datas)

def getwalletbalance():
    client = btcclient(setting.traceback_limit, setting.btc_conn)
    ret = client.getwalletbalance()
    assert ret.state == error.SUCCEED, "getwalletbalance failed"
    print("wallet balance:{}".format(ret.datas))

def getwalletaddressbalance(address):
    client = btcclient(setting.traceback_limit, setting.btc_conn)
    ret = client.getwalletaddressbalance(address)
    assert ret.state == error.SUCCEED, " getwalletaddressbalance failed"
    print("wallet balance:{}".format(ret.datas))

args = {"help"                  :   "dest: show arg list. format: --help",
        "sendtoaddress-"        :   "dest: send to address.format: --sendtoaddress \"address, amount\"",
        "sendexproofstart-"     :   "dest: create new exchange start proof. format: --sendexproofstart \"fromaddress, toaddress, amount, vaddress, sequence, vtoken\"",
        "sendexproofend-"       :   "dest: create new exchange end proof. format: --sendexproofend \"fromaddress, toaddress, vaddress, sequence, vamount, version\"",
        "sendexproofmark-"      :   "dest: create new exchange mark proof. format: --sendexproofmark \"fromaddress, toaddress, toamount, vaddress, sequence, version\"",
        "generatetoaddress-"    :   "dest: generate new block to address. format: --generatetoaddress \"count, address\"",
        "listunspent-"          :   "dest: returns array of unspent transaction outputs. format: --listunspent\"minconf, maxconf, addresses, include_unsafe, query_options\"",
        "listexproofforstart-"  :   "dest: returns array of proof state is start . format: --listexproofforstart\"receiver\"",
        "listexproofforend-"    :   "dest: returns array of proof state is end . format: --listexproofforend\"receiver\"",
        "listexproofformark-"   :   "dest: returns array of proof state is mark . format: --listexproofformark\"receiver\"",
        "btchelp"               :   "dest: returns bitcoin-cli help. format: --btchelp",
        "getwalletbalance"      :   "dest: returns wallet balance. format: --getwalletbalance",
        "getwalletaddressbalance-"      :   "dest: returns wallet target address's balance. format: --getwalletaddressbalance \"address\"",
        }
args_info = {
        }

def show_args():
    global args
    for key in args.keys():
        print("{}{} \n\t\t\t\t{}".format("--", key.replace('-', ''), args[key].replace('\n', '')))

def exit_error_arg_list(arg):
    print(args["{}-".format(arg.replace('--', ''))])
    sys.exit(2)

def show_arg_info(info):
    print(info)

def run(argc, argv):
    global args, args_info
    try:
        argfmt = list(args.keys())

        logger.debug("start violas.main")
        if argc == 0:
            show_args()
            sys.exit(2)
        if argv[0] == "help" and argc == 2:
            if argv[1] in argfmt:
                show_arg_info("--{} \n\t{}".format(argv[1], args[argv[1]].replace("format:", "\n\tformat:")))
            else:
                show_arg_info("--{} \n\t{}".format(argv[1], args["{}-".format(argv[1])].replace("format:", "\n\tformat:")))
            sys.exit(2)

        opts, err_args = getopt.getopt(argv, "ha:b:s", [arg.replace('-', "=") for arg in argfmt])
    except getopt.GetoptError as e:
        logger.error(e)
        sys.exit(2)
    except Exception as e:
        logger.error(e)
        sys.exit(2)

    #argument start for --
    if len(err_args) > 0:
        show_arg_info("arguments format is invalid. {}".format([ "--" + arg.replace('-', "") for arg in argfmt]))

    for opt, arg in opts:
        if len(arg) > 0:
            arg_list = "{}".format(arg).split(",")
            
            arg_list = [sub.strip() for sub in arg_list]

            show_arg_info("opt = {}, arg = {}".format(opt, arg_list))
        if opt in ( "--help"):
            show_args()
            sys.exit(2)
        elif opt in ("--sendtoaddress"):
            if len(arg_list) != 2:
                show_arg_info(args["{}-".format(opt.replace('--', ''))])
                sys.exit(2)
            ret = sendtoaddress(arg_list[0], arg_list[1])
        elif opt in ("--sendexproofstart"):
            if len(arg_list) != 6:
                exit_error_arg_list(opt)
            ret = sendexproofstart(arg_list[0], arg_list[1], float(arg_list[2]), arg_list[3], int(arg_list[4]), arg_list[5])
        elif opt in ("--sendexproofend"):
            if len(arg_list) != 6:
                exit_error_arg_list(opt)
            ret = sendexproofend(arg_list[0], arg_list[1], arg_list[2], int(arg_list[3]), int(arg_list[4]), int(arg_list[5]))
        elif opt in ("--sendexproofmark"):
            if len(arg_list) != 6:
                exit_error_arg_list(opt)
            ret = sendexproofmark(arg_list[0], arg_list[1], arg_list[2], arg_list[3], int(arg_list[4]), int(arg_list[5]))
        elif opt in ("--generatetoaddress"):
            if len(arg_list) != 2:
                exit_error_arg_list(opt)
                sys.exit(2)
            ret = generatetoaddress(int(arg_list[0]), arg_list[1])
        elif opt in ("--listunspent"):
            if len(arg_list) != 5 and len(arg_list) != 2:
                exit_error_arg_list(opt)
                sys.exit(2)
            if len(arg_list) != 2:
                ret = listunspent(int(arg_list[0]), int(arg_list[1]), arg_list[2], arg_list[3], arg_list[4])
            else:
                ret = listunspent(int(arg_list[0]), int(arg_list[1]))
        elif opt in ("--listexproofforstart"):
            if len(arg_list) != 1:
                exit_error_arg_list(opt)
                sys.exit(2)
            ret = listexproofforstart(arg_list[0])
        elif opt in ("--listexproofforend"):
            if len(arg_list) != 1:
                exit_error_arg_list(opt)
                sys.exit(2)
            ret = listexproofforend(arg_list[0])
        elif opt in ("--listexproofformark"):
            if len(arg_list) != 1:
                exit_error_arg_list(opt)
                sys.exit(2)
            ret = listexproofformark(arg_list[0])
        elif opt in ("--btchelp"):
            ret = btchelp()
        elif opt in ("--getwalletbalance"):
            ret = getwalletbalance()
        elif opt in ("--getwalletaddressbalance"):
            if len(arg_list) != 1:
                exit_error_arg_list(opt)
                sys.exit(2)
            ret = getwalletaddressbalance(arg_list[0])

    logger.debug("end manage.main")

if __name__ == "__main__":
    run(len(sys.argv) - 1, sys.argv[1:])
