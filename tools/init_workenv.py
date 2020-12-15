#!/usr/bin/python3
import operator
import sys, getopt
import json
import os
sys.path.append(os.getcwd())
sys.path.append("..")
import log
import log.logger
import stmanage
import comm_funs
from enum import Enum
from vlsopt.violasclient import (
        violasclient, 
        violaswallet
        )
from comm.parseargs import parseargs
from comm.values import (
        VIOLAS_ADDRESS_LEN
        )
from dataproof import dataproof

#module name
name="initworkenv"
chain = "violas"
wallet_name="vwallet"
logger = log.logger.getLogger(name)
token_min_amount = {
        "VLS": 1_00_0000,
        }

parent_vasp_address = "a5eeb37371bb939845a62bcaa1c2b41f"
token_list = ["VLS", "USDT", "BTC"]
opt_list = ["e2vm", "v2em", "v2bm", "b2vm"]

def get_violasclient():
    if chain == "libra":
        return violasclient(name, stmanage.get_libra_nodes(), chain)
    return violasclient(name, stmanage.get_violas_nodes(), chain)

def get_violaswallet():
    return violaswallet(name, dataproof.wallets(chain), chain)

def get_parent_address():
    return parent_vasp_address

def get_token_list(vclient, stmanage):
    global token_list
    if not token_list or len(token_list) <= 0:
        token_list = stmanage.get_support_token_id(chain)
    for token_id in token_list:
        assert vclient.token_id_effective(token_id).datas, f"token id: {token_id} is invalid." 
    return token_list

def get_opt_list(stmanage):
    global opt_list
    if not opt_list or len(opt_list) <= 0:
        opt_list = stmanage.get_support_mods_info()
    return opt_list

def use_tokens(*args):
    global token_list
    token_list = list(args)
    print(*args)

def use_opts(*args):
    global opt_list
    opt_list = args

def init_all():
    logger.debug("***************************************init workenv start*****************************")
    vclient = get_violasclient()
    wclient = get_violaswallet()

    token_list = get_token_list(vclient, stmanage)
    opt_list = get_opt_list(stmanage)
    parent_vasp_address = get_parent_address()

    #get support opt-type list id for chain

    logger.debug(f"opt list: {opt_list}")
    logger.debug(f"token_list: {token_list}")
    logger.debug(f"parent vasp address: {parent_vasp_address}")
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
        for token_id in token_list:
            minamount = token_min_amount.get(token_id, 0)
            if len(addresses) > 0:
                comm_funs.init_address_list(vclient, wclient, parent_vasp_address, addresses, token_id, minamount = minamount, gas_token_id = "VLS")


#test use: init client address
def init_one(address):
    vclient = get_violasclient()
    wclient = get_violaswallet()

    token_list= get_token_list(vclient, stmanage)
    parent_vasp_address = get_parent_address()
    btc_token_id = "BTC"

    logger.debug(f"token_list: {token_list}")
    logger.debug(f"parent vasp address: {parent_vasp_address}")
    print(f"{address} role name: {vclient.get_account_role_name(address)}")
    for token_id in token_list:
        minamount = token_min_amount.get(token_id, 0)
        print(f"fill token {token_id} amount to {minamount}")
        comm_funs.init_address_list(vclient, wclient, parent_vasp_address, [address], token_id, minamount = minamount)

def init_args(pargs):
    pargs.append("help", "show arg list.")
    pargs.append("conf", "config file path name. default:bvexchange.toml, find from . and /etc/bvexchange/", True, "toml file", priority = 5)
    pargs.append("wallet", "inpurt wallet file or mnemonic", True, "file name/mnemonic", priority = 13, argtype = parseargs.argtype.STR)
    pargs.append("token_list", f"inpurt support token list. \"\": get tokens from configure file, if not use this arg, use default: {token_list}.", True, optional_arglist = json.dumps(stmanage.get_support_token_id("violas")), priority = 13, callback = use_tokens)
    pargs.append("opt_list", f"inpurt support mods list. \"\": get opts(dtypes) from configure file, if not use this arg, use default:{opt_list}.", True, optional_arglist = json.dumps(stmanage.get_support_dtypes()), priority = 13, callback = use_opts)
    pargs.append(init_all, "init all address.")
    pargs.append(init_one, "init target address")

def run(argc, argv):
    global chain
    try:
        logger.debug("start violas.main")
        #--conf must be first
        if stmanage.get_conf_env() is None:
            stmanage.set_conf_env("../bvexchange.toml") 

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

    print(opts)
    for opt, arg in opts:

        arg_list = []
        if len(arg) > 0:
            count, arg_list = pargs.split_arg(opt, arg)

        print("opt = {}, arg = {}".format(opt, arg_list))
        if pargs.is_matched(opt, ["chain"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            chain = arg_list[0]
        elif pargs.is_matched(opt, ["conf"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            stmanage.set_conf_env(arg_list[0])
        elif pargs.is_matched(opt, ["wallet"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            dataproof.wallets.update_wallet(chain, arg_list[0])
        elif pargs.has_callback(opt):
            pargs.callback(opt, *arg_list)
        else:
            raise Exception(f"not found matched opt: {opt}")


    logger.debug("end manage.main")

if __name__ == "__main__":
    run(len(sys.argv) - 1, sys.argv[1:])
