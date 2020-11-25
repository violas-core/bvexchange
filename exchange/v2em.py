#!/usr/bin/python3
import operator
import sys, os
import json
sys.path.append(os.getcwd())
sys.path.append("..")
import stmanage
from comm.result import result, parse_except
from db.dblocal import dblocal as localdb
from comm.error import error
from exchange.exmap import exmap
from comm.values import (
        datatypebase as datatype, 
        trantypebase as trantype
        )

#load logging
class v2em(exmap):    
    def __init__(self, name, 
            dtype, 
            vlsnodes, 
            ethnodes, 
            proofdb, 
            receivers, 
            senders,
            **kwargs
            ):

        kwargs.update({self.create_nodes_key(trantype.ETHEREUM.value) : ethnodes})
        kwargs.update({self.create_nodes_key(trantype.VIOLAS.value) : vlsnodes})
        exmap.__init__(self, name, dtype, \
                proofdb, receivers, senders,\
                trantype.VIOLAS, trantype.ETHEREUM, \
                **kwargs)
        self.__init_exec_states()

    def __init_exec_states(self):
        self.append_property("use_exec_update_db_states", 
                            [state for state in localdb.state])
    def __del__(self):
        pass
    

def main():
       print("start main")
       stmanage.set_conf_env("../bvexchange.toml")
       mod = "v2em"
       dtype = "v2em"
       obj = v2em(mod, 
               dtype,
               stmanage.get_violas_nodes(), 
               stmanage.get_eth_nodes(),
               stmanage.get_db(dtype), 
               list(set(stmanage.get_receiver_address_list(dtype, "violas", False))),
               list(set(stmanage.get_sender_address_list(dtype, "ethereum", False))),
               )
       ret = obj.start()
       if ret.state != error.SUCCEED:
           print(ret.message)

if __name__ == "__main__":
    main()
