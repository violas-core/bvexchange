#!/usr/bin/python3
'''
clean all db datas
'''
import operator
import sys,os,getopt
sys.path.append(os.getcwd())
sys.path.append("..")
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
import log
import log.logger
import stmanage
from comm.result import result, parse_except
from db.dbvbase import dbvbase
from comm.parseargs import parseargs
from comm.functions import (
        json_print,
        )
from dataproof import dataproof
from comm.values import (
        PACKAGE_ROOT_PATH,
        )


#module name
name="cleanlocaldbs"


logger = log.logger.getLogger(name)

work_mod  = {}
def clean_db(db):
    logger.info(f"start clean db: {db}")
    try:
        if db in work_mod:
            os.unlink(work_mod[db])
            del work_mod[db]
    except Exception as e:
        logger.error(e)
        return
    logger.info(f"clean succeed db: {db}")


def list_valid_mods():
    loads_mods()
    valid_mods = ["all"]
    valid_mods.extend(list(work_mod.keys()))
    return valid_mods


def run_mods(mods):
    valid_mods = list_valid_mods()
    for mod in mods:
        if mod is None or mod not in valid_mods:
            raise Exception(f"mod({mod}) is invalid {valid_mods}.")

    logger.info(f"clean mods: {mods}")

    logger.warning(f"will clean: {mods}")
    for i in range(3):
        run_cmd = input(f"continue clean ...? (yes/no)")
        if run_cmd in ("y", "yes"):
            break
        elif run_cmd in ("n", "no"):
            return
    else:
        logger.warning("max times, retry run it.")
        return 

    for mod in mods:
        clean_db(mod)

def show_exec_args():
    pass

def get_include_mods(mods):
    work_mods = []
    for mod in mods:
        if mod == "all":
            work_mods = list_valid_mods()
            work_mods.remove("all")
            break
        work_mods.append(mod)
    return work_mods

def __get_localdb_path():
    localdb_path = os.path.abspath(
            os.path.join(
                os.path.join(PACKAGE_ROOT_PATH, stmanage.get_datas_root_path()), 
                "localdbs")
            )
    return localdb_path

def show_target_path():
    print(f"{__get_localdb_path()}")

def loads_mods():
    global work_mod
    work_mod.clear()
    localdb_path = __get_localdb_path()
    for root,dirs,files in os.walk(localdb_path):
        for file in files:
            path = os.path.join(root,file)
            name = os.path.splitext(file)[0]
            work_mod.update({name : path})
    return work_mod

def show_mods():
    mods = list_valid_mods()
    print(f"**count: {len(mods)}\n")
    [print(f"{key} : {index}") for index, key in  enumerate(mods)]

def init_args(pargs):
    pargs.clear()
    mods = list_valid_mods()
    pargs.append("help", "show arg list.")
    pargs.append("conf", "config file path name. default:bvexchange.toml, find from . and /etc/bvexchange/", True, "toml file", priority = 5)
    pargs.append("mod", "include infos", True, mods, priority = 20)
    pargs.append("exclude", "exclude infos", True, [ mod for mod in mods if mod not in ("all")], priority = 30)
    pargs.append(show_mods, "show localdb list.", priority = 30)
    pargs.append(show_target_path, "show localdb root path.", priority = 30)

def run(argc, argv, exit = True):

    pargs = parseargs(exit = exit)
    try:
        init_args(pargs)
        if pargs.show_help(argv): 
            return
        opts, err_args = pargs.getopt(argv)
    except getopt.GetoptError as e:
        logger.error(str(e))
        if exit:
            sys.exit(2)
        return
    except Exception as e:
        logger.error(str(e))
        if exit:
            sys.exit(2)
        return

    if err_args is None or len(err_args) > 0:
        pargs.show_args()
        return

    names = [opt for opt, arg in opts]
    pargs.check_unique(names)

    exclude_mods =  []
    include_mods =  list_valid_mods()

    for opt, arg in opts:
        count, arg_list = pargs.split_arg(opt, arg)
        if pargs.is_matched(opt, ["conf"]):
            pargs.exit_check_opt_arg(opt, arg, 1)
            stmanage.set_conf_env(arg)
        elif pargs.is_matched(opt, ["help"]):
            init_args(pargs)
            pargs.show_args()
            return
        elif pargs.is_matched(opt, ["exclude"]):
            pargs.exit_check_opt_arg_min(opt, arg, 1)
            exclude_mods = list(arg_list)
        elif pargs.is_matched(opt, ["mod"]) :
            pargs.exit_check_opt_arg_min(opt, arg, 1)
            include_mods = get_include_mods(arg_list)
        elif pargs.has_callback(opt):
            pargs.callback(opt, *arg_list)
            return 

    target_mods = set(include_mods).difference(set(exclude_mods))
    show_exec_args()
    run_mods(target_mods)
    return
if __name__ == "__main__":
    stmanage.set_conf_env("../bvexchange.toml")
    print(sys.argv)
    run(len(sys.argv) - 1, sys.argv[1:])
