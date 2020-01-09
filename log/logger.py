import logging
import logging.config
import log.config


def __init__():
    print("logger.__init__")

def getLogger(name):

    log.config.config["handlers"]["file"]["filename"]=f"{name}.log"
    default = log.config.config.get("loggers").get("bvelog")
    if name not in log.config.config.get("loggers"):
        log.config.config.get("loggers")[name] = default

    logging.config.dictConfig(log.config.config)
    logger = logging.getLogger(name)

    return logger

