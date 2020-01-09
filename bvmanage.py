#!/usr/bin/python3
import sys, getopt, os
#os.chdir(os.path.dirname(sys.argv[0]))
import log 
import json
import log.logger
from comm.parseargs import parseargs
import bvexchange

name = "bvexchange"
logger = log.logger.getLogger(name)


def init_args(pargs):
    pargs.append("help", "show args info")
    pargs.append("mod", "run mod", True, ["all", "b2v", "v2b", "vfilter", "vproof"])

def main(argc, argv):
    pargs = parseargs()
    try:
        logger.debug("start manage.main")
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
        count, arg_list = pargs.split_arg(arg)
        if pargs.is_matched(opt, ["mod"]) :
            if count < 1:
                pargs.exit_error_opt(opt)
            bvexchange.run(arg_list)
    logger.debug("end manage.main")

if __name__ == '__main__':
    main(len(sys.argv) - 1, sys.argv[1:])
