#!/usr/bin/python3
import sys, getopt, os
import log 
import json
import log.logger
import bvexchange
import stmanage
from comm.parseargs import parseargs
from comm.version import version
from comm.functions import json_print
from tools import show_workenv
from dataproof import dataproof

name = "bvexchange"
logger = log.logger.getLogger(name)

def init_args(pargs):
    pargs.clear()
    pargs.append("help", "show args info", priority = 11)
    pargs.append("version", "show version info")
    pargs.append("mod", "run mod", True, bvexchange.list_valid_mods())
    pargs.append("info", "show info", True, show_workenv.list_valid_mods())
    pargs.append("show_conf", "show data proof info for config", True, "[all/target config]", priority = 30)
    pargs.append("conf", "config file path name. default:bvexchange.toml, find from . and /etc/bvexchange/", True, "toml file", priority = 10)
    pargs.append("eth_usd_chain", "load eth contract info(address, decimals). default:local abi, if set it will load from ethereum vlsmproofmain(contract) load", priority = 20)
    pargs.append("help_exe_args", "show execute args for mods", priority = 20)
    pargs.append("vwallet", "file or mnemonic:num for violas wallet", True, "[file/mnemonic:num]", priority = 20, argtype = parseargs.argtype.STR)
    pargs.append("lwallet", "file or mnemonic:num for violas wallet", True, "[file/mnemonic:num]", priority = 20, argtype = parseargs.argtype.STR)
    pargs.append("ewallet", "file or mnemonic:num for ethereum wallet", True, "[file/mnemonic:num]", priority = 20, argtype = parseargs.argtype.STR)
    pargs.append("bwallet", "file or address:privkey list for btc wallet, format: \"ADDRESS:PRIVKEY,ADDRESS:PRIVKEY\"", True, "[file/address:privkey]", priority= 20, argtype = parseargs.argtype.STR)

def show_exec_args():
    logger.debug(f'"eth_usd_chain": dataproof.configs("eth_usd_chain")')

def main(argc, argv):

    pargs = parseargs()
    try:
        logger.debug("start manage.main")
        #--conf must be first
        if stmanage.get_conf_env() is None:
            stmanage.set_conf_env_default() 

        init_args(pargs)
        pargs.show_help(argv)
        opts, err_args = pargs.getopt(argv)
    except getopt.GetoptError as e:
        logger.error(str(e))
        sys.exit(2)
    except Exception as e:
        logger.error(str(e))
        sys.exit(2)

    if err_args is None or len(err_args) > 0:
        pargs.show_args()

    names = [opt for opt, arg in opts]
    pargs.check_unique(names)

    for opt, arg in opts:
        count, arg_list = pargs.split_arg(opt, arg)
        if pargs.is_matched(opt, ["conf"]):
            pargs.exit_check_opt_arg(opt, arg, 1)
            stmanage.set_conf_env(arg)
        elif pargs.is_matched(opt, ["help"]):
            init_args(pargs)
            pargs.show_help(argv)
            return
        elif pargs.is_matched(opt, ["show_conf"]):
            if count == 0 or (count == 1 and arg_list[0] == "all"):
                json_print(dataproof.configs.datas)
            else:
                json_print(dataproof.configs(arg_list[0]))
            return
        elif pargs.is_matched(opt, ["vwallet"]):
            pargs.exit_check_opt_arg(opt, arg, 1)
            dataproof.wallets.update_wallet("violas", arg_list[0])
        elif pargs.is_matched(opt, ["lwallet"]):
            pargs.exit_check_opt_arg(opt, arg, 1)
            dataproof.wallets.update_wallet("libra", arg_list[0])
        elif pargs.is_matched(opt, ["ewallet"]):
            pargs.exit_check_opt_arg(opt, arg, 1)
            dataproof.wallets.update_wallet("ethereum", arg_list[0])
        elif pargs.is_matched(opt, ["bwallet"]):
            pargs.exit_check_opt_arg(opt, arg, 1)
            dataproof.wallets.update_wallet("btc", arg_list[0])
        elif pargs.is_matched(opt, ["eth_usd_chain"]):
            dataproof.configs.set_config("eth_usd_chain", True)
        elif pargs.is_matched(opt, ["help_exe_args"]):
            dataproof.configs.set_config("help_exe_args", True)
        elif pargs.is_matched(opt, ["version"]) :
            logger.debug(f"version:{version()}")
            return
        elif pargs.is_matched(opt, ["mod"]) :
            pargs.exit_check_opt_arg_min(opt, arg, 1)
            logger.debug(f"arg_list:{arg_list}")
            show_exec_args()
            bvexchange.run(arg_list)
            return
        elif pargs.is_matched(opt, ["info"]) :
            pargs.exit_check_opt_arg_min(opt, arg, 1)
            logger.debug(f"arg_list:{arg_list}")
            show_workenv.run(arg_list)
            return
            
    #get run mods from config file
    run_mods = []
    dtypes = stmanage.get_run_mods()
    for dtype in dtypes:
        for mod in bvexchange.list_valid_mods():
            if mod.startswith(dtype):
                run_mods.append(mod)
    if run_mods:
        bvexchange.run(run_mods)

    logger.debug("end manage.main")

if __name__ == '__main__':
    main(len(sys.argv) - 1, sys.argv[1:])
