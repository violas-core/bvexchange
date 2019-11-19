import logging
import logging.config
import log.config


def __init__():
    print("logger.__init__")

def getLogger(name):
    logging.config.dictConfig(log.config.config)
    logger = logging.getLogger(name)

    return logger

