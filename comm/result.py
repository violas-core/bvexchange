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
        sign = ""
        sign_key = ""
        sign_key_id = ""
        
        def __init__(self, state = None, message = None, datas = None):
            self.state = state 
            self.message = message
            self.datas = datas
            self.sign = ""
            self.sign_key = ""
            self.sign_key_id = ""

        def to_map(self):
            return self.to_json()
        
        def __repr__(self):
            return f"state={self.state.name}, message={self.message}, datas:{self.datas}, sign:{self.sign}, sign_key:{self.sign_key}, sign_key_id:{self.sign_key_id}"

        def to_json(self):
            return {"state":self.state.name, "message":self.message, "datas":self.datas}

        def to_json_with_sign(self):
            return {"state":self.state.name, "message":self.message, "datas":self.datas, "sign": self.sign, "sign_key": self.sign_key, "sign_key_id": self.sign_key_id, "sign_datas": self.to_hex()}

        def to_hex(self):
            return json.dumps(self.to_json()).encode().hex()

        def dumps(self):
            return json.dumps(self.to_json())

        def loads(self, datas):
            if isinstance(datas, str):
                self.load_json(json.loads(datas))
            elif isinstance(datas, dict):
                self.load_json(datas)
            else:
                raise ValueError("datas type invalid")
            return self

        def load_json(self, data):
            self.state = error(data.get("state").lower())
            self.message = data.get("message")
            self.datas = data.get("datas")
            self.sign = data.get("sign")
            self.sign_key = data.get("sign_key")
            self.sign_key_id = data.get("sign_key_id")

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


