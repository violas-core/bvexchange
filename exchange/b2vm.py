#!/usr/bin/python3
import operator
import sys, os
import json
sys.path.append(os.getcwd())
sys.path.append("..")
import log
import log.logger
import datetime
import stmanage
import requests
import comm
import comm.values
from comm.result import result, parse_except
from comm.error import error
import vlsopt.violasclient
from enum import Enum
from exchange.vbmap import vbmap


#load logging
class b2vm(vbmap):    
    def __init__(self, name, 
            dtype, 
            btcnodes, 
            vlsnodes, 
            proofdb, 
            receivers, 
            senders 
            ):

        vbmap.__init__(self, name, dtype, btcnodes, vlsnodes,  \
                proofdb, receivers, senders,\
                "btc", "violas")

    def __del__(self):
        pass
    

def main():
       print("start main")
       stmanage.set_conf_env("../bvexchange.toml")
       mod = "b2vm"
       dtype = "b2vm"
       obj = v2bm(mod, 
               dtype,
               stmanage.get_btc_nodes(),
               stmanage.get_violas_nodes(), 
               stmanage.get_db(dtype), 
               list(set(stmanage.get_receiver_address_list(dtype, "btc", False))),
               list(set(stmanage.get_sender_address_list(dtype, "violas", False))),
               )
       ret = obj.start()
       if ret.state != error.SUCCEED:
           print(ret.message)

if __name__ == "__main__":
    main()
