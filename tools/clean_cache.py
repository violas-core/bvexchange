#!/usr/bin/python3
'''
clean all db datas
'''
import operator
import sys,os
sys.path.append(os.getcwd())
sys.path.append("..")
import log
import log.logger
import traceback
import datetime
import sqlalchemy
import random
import redis
from comm.error import error
from comm.result import result, parse_except
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, UniqueConstraint, Index, String
from db.dbvbase import dbvbase
from enum import Enum
import stmanage


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
            raise Exception(f"mod({mod}) is invalid {valid_mods}.")

    work_mods = {}
    for mod in mods:
        if mod == "all":
            for wm in work_mod:
                clean_db(name, wm.name.lower())
            break

        clean_db(name, mod.lower())

def main(argc, argv):

    try:
        stmanage.set_conf_env("../bvexchange.toml")
        if argc < 1:
            raise Exception(f"argument is invalid. args:{list_valid_mods()}")
        run(argv)
    except Exception as e:
        parse_except(e)
    finally:
        logger.critical("main end")

if __name__ == "__main__":
    main(len(sys.argv) - 1, sys.argv[1:])
