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
from comm.result import result, parse_except
from comm.error import error
from db.dblocal import dblocal as localdb
from exchange.x2vswap import x2vswap

#module self.name
#name="l2v"
wallet_name = "vwallet"

#load logging
class l2v(x2vswap):    
    def __init__(self, name, 
            dtype, 
            vlsnodes, 
            lbrnodes, 
            proofdb, 
            receivers, 
            senders, 
            swap_module,
            swap_owner, 
            **kwargs):

        '''libra Coin1/Coin2 swap to violas stable token 
            @dtype : opttype
            @vlsnodes: violas node configure
            @lbrnodes: libra nodes configure
            @proofdb: violas proof configure, no-use
            @receivers: btc address, get valid swap transaction
            @senders: violas senders address, use this address to transfer(diff chain)
            @combine: btc address, change state transaction's payer
            @swap_module: swap module address
            @swap_owner: swap owner address
        '''
        x2vswap.__init__(self, name, dtype, \
                None, vlsnodes, lbrnodes, \
                proofdb, receivers, senders, \
                swap_module, swap_owner,\
                "libra", "violas", \
                **kwargs)
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
       mod = "l2vgbp"
       dtype = "l2vgbp"
       obj = l2v(mod, 
               dtype,
               stmanage.get_violas_nodes(), 
               stmanage.get_libra_nodes(),
               stmanage.get_db(dtype), 
               list(set(stmanage.get_receiver_address_list(dtype, "libra", False))),
               list(set(stmanage.get_sender_address_list(dtype, "violas", False))),
               stmanage.get_swap_module(),
               stmanage.get_swap_owner(),
               )
       ret = obj.start()
       if ret.state != error.SUCCEED:
           print(ret.message)

if __name__ == "__main__":
    main()
