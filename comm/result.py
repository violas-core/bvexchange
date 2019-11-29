#!/usr/bin/python3

import sys
from . import error

name="result"
error = error.error
class result:
        state = error.SUCCEED
        message = ""
        datas = ""
        
        def __init__(self, state, message = None, datas = None):
            self.state = state 
            self.message = message
            self.datas = datas

