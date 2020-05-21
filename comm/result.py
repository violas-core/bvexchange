#!/usr/bin/python3

import sys, json
from . import error
sys.path.append("..")
import traceback
import log
import log.logger
name="result"
error = error.error
name="except" 
class result:
        state = error.SUCCEED
        message = ""
        datas = ""
        
        def __init__(self, state = None, message = None, datas = None):
            self.state = state 
            self.message = message
            self.datas = datas

        def to_map(self):
            return {"state": "self.state.name", "message":self.message, "datas":self.datas}
        
        def __repr__(self):
            return f"state={self.state.name}, message={self.message}, datas:{self.datas}"

        def to_json(self):
            return {"state":self.state.name, "message":self.message, "datas":self.datas}

        def load_json(self, data):
            self.state = error(data.get("state").lower())
            self.message = data.get("message")
            self.datas = data.get("datas")

def parse_except(e, msg = None, datas = None):
    try:
        e_type = error.EXCEPT
        print(traceback.format_exc(limit=10))
        if msg is None:
            msg = "Exception"
        if datas is None:
            datas = e
        ret = result(e_type, msg, datas)
        return ret
    except Exception as e: #at last
        ret = result(error.EXCEPT, "", e)
    return ret


