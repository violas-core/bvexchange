import logging
import logging.config
import log.config


def __init__():
    print("logger.__init__")

def getLogger():
    logging.config.dictConfig(log.config.config)
    logger = logging.getLogger("FileLogger")

    return logger

