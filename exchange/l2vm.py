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


#load logging
class l2vm(exmap):    
    def __init__(self, name, 
            dtype, 
            lbrnodes, 
            vlsnodes, 
            proofdb, 
            receivers, 
            senders 
            ):

        exmap.__init__(self, name, dtype, \
                None, vlsnodes, lbrnodes, None,\
                proofdb, receivers, senders,\
                "libra", "violas")

    def __del__(self):
        pass
    

def main():
       print("start main")
       stmanage.set_conf_env("../bvexchange.toml")
       mod = "l2vm"
       dtype = "l2vm"
       obj = l2vm(mod, 
               dtype,
               stmanage.get_libra_nodes(),
               stmanage.get_violas_nodes(), 
               stmanage.get_db(dtype), 
               list(set(stmanage.get_receiver_address_list(dtype, "libra", False))),
               list(set(stmanage.get_sender_address_list(dtype, "violas", False))),
               )
       ret = obj.start()
       if ret.state != error.SUCCEED:
           print(ret.message)

if __name__ == "__main__":
    main()
