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
#name="b2v"
wallet_name = "vwallet"

#load logging
class b2v(x2vswap):    
    def __init__(self, name, 
            dtype, 
            btcnodes, 
            vlsnodes, 
            proofdb, 
            receivers, 
            senders,
            combine, #btc address
            swap_module,
            swap_owner,
            **kwargs):

        '''bitcoin BTC swap to violas stable token 
            @dtype : opttype
            @btcnodes: btc node configure
            @vlsnodes: violas nodes configure
            @proofdb: violas proof configure, no-use
            @receivers: btc address, get valid swap transaction
            @senders: violas senders address, use this address to transfer(diff chain)
            @combine: btc address, change state transaction's payer
            @swap_module: swap module address
            @swap_owner: swap owner address
        '''
        x2vswap.__init__(self, name, dtype, \
                btcnodes, vlsnodes, None, \
                proofdb, receivers, senders, \
                swap_module, swap_owner,\
                "btc", "violas", \
                **kwargs)
        self.append_property("combine_account", combine)
        self.init_exec_states()

    def init_exec_states(self):

        self.append_property("use_exec_update_db_states", 
                [localdb.state.VSUCCEED, localdb.state.SSUCCEED])

        self.append_property("use_exec_failed_state", 
            [state for state in localdb.state \
                    if state not in [localdb.state.COMPLETE, \
                        localdb.state.VSUCCEED, \
                        localdb.state.SSUCCEED]])
        
        ret = self.get_record_from_localdb_with_state(self.use_exec_failed_state)
        if ret.state != error.SUCCEED:
            return ret
        excluded = []
        for receiver, datas in ret.datas.items():
            for data in datas:
                address_seq = data.get("tran_id").split("_")
                excluded.append({"address":address_seq[0], "sequence":address_seq[1]})

        setattr(self, "excluded", excluded)

def main():
       print("start main")
       stmanage.set_conf_env("../bvexchange.toml")
       dtype = "b2vusd"
       obj = b2v(dtype, 
               dtype,
               stmanage.get_btc_nodes(), 
               stmanage.get_violas_nodes(),
               stmanage.get_db(dtype), 
               list(set(stmanage.get_receiver_address_list(dtype, "btc", False))),
               list(set(stmanage.get_sender_address_list(dtype, "violas", False))),
               stmanage.get_combine_address(dtype, "btc", True),
               stmanage.get_swap_module(),
               stmanage.get_swap_owner()
               )
       ret = obj.start()
       if ret.state != error.SUCCEED:
           print(ret.message)

if __name__ == "__main__":
    main()
