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


#module name
name="cleancache"

logger = log.logger.getLogger(name)
class dbvclean(dbvbase):
    def __init__(self, name, host, port, db, passwd = None):
        dbvbase.__init__(self, name, host, port, db, passwd)

    def __del__(self):
        dbvbase.__del__(self)

work_mod  = dbvbase.dbindex 
def clean_db(name, db):
    logger.debug(f"clean db: {db}")
    dbconf = stmanage.get_db(db)
    dbclient = dbvclean(name, dbconf.get("host"), dbconf.get("port"), dbconf.get("db"), dbconf.get("password"))
    dbclient.flush_db()


def list_valid_mods():
    valid_mods = ["all"]
    for mod in work_mod:
        valid_mods.append(mod.name.lower())
    return valid_mods


def run(mods):
    valid_mods = list_valid_mods()
    for mod in mods:
        if mod is None or mod not in valid_mods:
            print(mod)
            raise Exception(f"mod({mod}) is invalid {valid_mods}.")

    logger.info(f"clean mods: {mods}")

    print(f"will clean: {mods}")
    for i in range(3):
        print(f"continue clean ...? (yes/no)")
        run_cmd = input()
        if run_cmd in ("y", "yes"):
            break
        elif run_cmd in ("n", "no"):
            return
    else:
        print("max times, retry run it.")
        return 

    for mod in mods:
        clean_db(name, mod.lower())

def init_args(pargs):
    pargs.clear()
    mods = list_valid_mods()
    pargs.append("help", "show arg list.")
    pargs.append("mod", "include infos", True, mods, priority = 20)
    pargs.append("exclude", "exclude infos", True, [ mod for mod in mods if mod not in ("all")], priority = 30)

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

    exclude_mods =  []
    include_mods =  list_valid_mods()

    for opt, arg in opts:
        count, arg_list = pargs.split_arg(opt, arg)
        if pargs.is_matched(opt, ["conf"]):
            pargs.exit_check_opt_arg(opt, arg, 1)
            stmanage.set_conf_env(arg)
        elif pargs.is_matched(opt, ["help"]):
            init_args(pargs)
            pargs.show_help(argv)
            return
        elif pargs.is_matched(opt, ["exclude"]):
            pargs.exit_check_opt_arg_min(opt, arg, 1)
            exclude_mods = list(arg_list)
            print(exclude_mods)
        elif pargs.is_matched(opt, ["mod"]) :
            pargs.exit_check_opt_arg_min(opt, arg, 1)
            include_mods = get_include_mods(arg_list)

    run_mods = set(include_mods).difference(set(exclude_mods))
    show_exec_args()
    run(run_mods)
    return
if __name__ == "__main__":
    main(len(sys.argv) - 1, sys.argv[1:])
