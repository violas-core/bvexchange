#!/usr/bin/python3
import operator
import sys, os
import json
sys.path.append(os.getcwd())
sys.path.append("..")
import stmanage
from comm.result import result, parse_except
from comm.error import error
from exchange.exmap import exmap
from comm.values import (
        datatypebase as datatype, 
        trantypebase as trantype
        )

#load logging
class v2bm(exmap):    
    def __init__(self, name, 
            dtype, 
            vlsnodes, 
            btcnodes, 
            proofdb, 
            receivers, 
            senders,
            **kwargs
            ):

        kwargs.update({self.create_nodes_key(trantype.VIOLAS.value) : vlsnodes})
        kwargs.update({self.create_nodes_key(trantype.BTC.value) : btcnodes})
        exmap.__init__(self, name, dtype, \
                proofdb, receivers, senders,\
                trantype.VIOLAS, trantype.BTC, \
                **kwargs)

    def __del__(self):
        pass
    

def main():
       print("start main")
       stmanage.set_conf_env("../bvexchange.toml")
       mod = "v2bm"
       dtype = "v2bm"
       obj = v2bm(mod, 
               dtype,
               stmanage.get_violas_nodes(), 
               stmanage.get_btc_nodes(),
               stmanage.get_db(dtype), 
               list(set(stmanage.get_receiver_address_list(dtype, "violas", False))),
               list(set(stmanage.get_sender_address_list(dtype, "btc", False))),
               )
       ret = obj.start()
       if ret.state != error.SUCCEED:
           print(ret.message)

if __name__ == "__main__":
    main()
