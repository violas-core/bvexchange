#!/usr/bin/python3
import sys, getopt
import log 
import json
import log.logger


name = "bvelog"
logger = log.logger.getLogger(name)
params = ["-h ",
          "-a",
          "-b",
          "-s"
        ]
def main(argc, argv):
    try:
        logger.debug("start manage.main")
        if argc == 0:
            logger.critical(json.dumps(params))
        opts, args = getopt.getopt(argv, "ha:b:s")
    except getopt.GetoptError as e:
        logger.error(json.dumps(params))
        sys.exit(2)
    except Exception as e:
        logger.error(e)
        sys.exit(2)

    if len(opts) == 0:
            logger.critical(json.dumps(params))

    for opt, arg in opts:
        if opt == '-h':
            logger.info(json.dumps(params))
        elif opt == '-a':
            logger.debug(arg)
        elif opt == '-b':
            logger.debug(arg)
        elif opt == '-s':
            logger.debug(arg)
    logger.debug("end manage.main")

if __name__ == '__main__':
    main(len(sys.argv) - 1, sys.argv[1:])
