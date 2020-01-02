import logging
import logging.config
import log.config


def __init__():
    print("logger.__init__")

def getLogger(name):

    logger_name = name
    default = log.config.config.get("loggers").get("bvelog")
    if logger_name not in log.config.config.get("loggers"):
        log.config.config.get("loggers")[logger_name] = default

    logging.config.dictConfig(log.config.config)
    logger = logging.getLogger(logger_name)

    return logger

