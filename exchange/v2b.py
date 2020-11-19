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
#name="v2b"
wallet_name = "vwallet"

class v2b(v2xswap):    
    def __init__(self, 
            name, 
            dtype, 
            vlsnodes, 
            btcnodes, 
            proofdb, 
            receivers, 
            senders, 
            combine, 
            swap_module,
            swap_owner,
            **kwargs):
        ''' violas stable token swap to bitcoin BTC
            @dtype : opttype
            @vlsnodes: violas nodes configure
            @btcnodes: btc node configure
            @proofdb: violas proof configure
            @receivers: violas receivers address
            @senders: btc address, use this address to transfer
            @combine: violas address, use this address store swap token 
            @swap_module: swap module address
            @swap_owner: swap owner address
        '''
        v2xswap.__init__(self, name, dtype, \
                btcnodes, vlsnodes, None, \
                proofdb, receivers, senders, combine, \
                swap_module, swap_owner,\
                "violas", "btc", \
                **kwargs)

        self.init_exec_states()

    def init_exec_states(self):

        self.append_property("use_exec_update_db_states", 
                [localdb.state.VSUCCEED, localdb.state.SSUCCEED])

        self.append_property("use_exec_failed_state", 
            [state for state in localdb.state \
                    if state not in [localdb.state.COMPLETE, \
                        localdb.state.VSUCCEED, \
                        localdb.state.SSUCCEED, \
                        localdb.state.PSUCCEED]])


def main():
       print("start main")
       
       stmanage.set_conf_env("../bvexchange.toml")
       mod = "v2b"
       dtype = "v2b"
       obj = v2b(mod, 
               dtype,
               stmanage.get_violas_nodes(), 
               stmanage.get_btc_nodes(),
               stmanage.get_db(dtype), 
               list(set(stmanage.get_receiver_address_list(dtype, "violas", False))),
               list(set(stmanage.get_sender_address_list(dtype, "btc", False))),
               stmanage.get_combine_address(dtype, "violas"),
               stmanage.get_swap_module(),
               stmanage.get_swap_owner()
               )
       ret = obj.start()
       if ret.state != error.SUCCEED:
           print(ret.message)

if __name__ == "__main__":
    main()
