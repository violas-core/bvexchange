#!/usr/bin/python3
import operator
import sys, getopt
from time import sleep
import json
import os
import time
import signal
sys.path.append(os.getcwd())
sys.path.append("..")
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
import log
import log.logger
import traceback
import datetime
import sqlalchemy
import stmanage
import requests
import comm
import comm.error
import comm.result
from comm.result import result
from comm.error import error
from comm.parseargs import parseargs
from comm.functions import (
    json_print,
    split_full_address,
    output_args_func
        )

from analysis import parse_transaction


def test_get_map_mods():
    print(parse_transaction.get_map_mods())

def setup():
    pass

if __name__ == "__main__":
    setup()
    pa = parseargs(globals())
    pa.test(sys.argv)


