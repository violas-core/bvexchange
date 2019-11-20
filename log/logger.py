import logging
import logging.config
import log.config


def __init__():
    print("logger.__init__")

def getLogger(name):
    logging.config.dictConfig(log.config.config)

    logger_name = "bvelog"

    if name == "dbb2v":
        logger_name = "b2vlog"
    elif name == "dbv2b":
        logger_name = "v2blog"

    logger = logging.getLogger(logger_name)

    return logger

