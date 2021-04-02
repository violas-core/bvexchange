#!/usr/bin/python3
import sys, os, operator, types
import json
sys.path.append("..")
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "./"))

from lbparseargs import (
        parseargs as parseargsbase
        )
#module name

class parseargs(parseargsbase):
    def __init__(self, globals = None, exit = True):
        parseargsbase.__init__(self, globals = globals, exit = exit)
