#!/usr/bin/python3
import operator
import sys, os
sys.path.append(os.getcwd())
sys.path.append("..")
import stmanage
from comm.result import result, parse_except
from comm.error import error
from db.dblocal import dblocal as localdb
from exchange.v2xswap import v2xswap

#module self.name
#name="v2l"
wallet_name = "vwallet"

class v2l(v2xswap):    
    def __init__(self, 
            name, 
            dtype, 
            vlsnodes, 
            lbrnodes, 
            proofdb, 
            receivers, 
            senders, 
            combine, 
            swap_module, 
            swap_owner):
        v2xswap.__init__(self, name, dtype, \
                None, vlsnodes, lbrnodes, \
                proofdb, receivers, senders, combine, \
                swap_module, swap_owner, \
                "violas", "libra")

        self.init_exec_states()

    def init_exec_states(self):
        self.append_property("use_exec_update_db_states", 
                [localdb.state.VSUCCEED, localdb.state.SSUCCEED])

        self.append_property("use_exec_failed_state", 
            [state for state in localdb.state \
                    if state not in [localdb.state.COMPLETE, \
                        localdb.state.VSUCCEED, \
                        localdb.state.SSUCCEED]])

def main():
       print("start main")
       
       stmanage.set_conf_env("../bvexchange.toml")
       mod = "v2l"
       dtype = "v2lusd"
       obj = v2l(mod, 
               dtype,
               stmanage.get_violas_nodes(), 
               stmanage.get_libra_nodes(),
               stmanage.get_db(dtype), 
               list(set(stmanage.get_receiver_address_list(dtype, "violas", False))),
               list(set(stmanage.get_sender_address_list(dtype, "libra", False))),
               stmanage.get_combine_address(dtype, "violas"),
               stmanage.get_swap_module(),
               stmanage.get_swap_owner()
               )
       ret = obj.start()
       if ret.state != error.SUCCEED:
           print(ret.message)

if __name__ == "__main__":
    main()
