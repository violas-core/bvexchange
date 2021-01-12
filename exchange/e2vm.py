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
class e2vm(exmap):    
    def __init__(self, name, 
            dtype, 
            ethnodes, 
            vlsnodes, 
            proofdb, 
            receivers, 
            senders,
            mapper,
            **kwargs
            ):

        kwargs.update({self.create_nodes_key(trantype.ETHEREUM.value) : ethnodes})
        kwargs.update({self.create_nodes_key(trantype.VIOLAS.value) : vlsnodes})
        exmap.__init__(self, name, dtype, \
                proofdb, receivers, senders,\
                trantype.ETHEREUM, trantype.VIOLAS, \
                **kwargs)
        self.__init_exec_states()
        self.set_contract_map_address(mapper)

    def __init_exec_states(self):
        self.append_property("use_exec_update_db_states", 
                            [state for state in localdb.state if state != localdb.state.COMPLETE])

    def set_contract_map_address(self, address):
        ret = self.ethereum_wallet.get_account(address)
        if ret.state != error.SUCCEED:
            raise Exception(f"get account failed.{ret.message}")
        
        self.ethereum_client.set_contract_map_account(ret.datas)

    def __del__(self):
        pass
    

def main():
       print("start main")
       stmanage.set_conf_env("../bvexchange.toml")
       try:
          dtype = "e2vm"
          obj = e2vm("e2vm",
                  dtype,
                  stmanage.get_eth_nodes(), 
                  stmanage.get_violas_nodes(),
                  stmanage.get_db(dtype), 
                  list(set(stmanage.get_receiver_address_list(dtype, trantype.ETHEREUM.value, False))),
                  list(set(stmanage.get_sender_address_list(dtype, trantype.VIOLAS.value, False))),
                  stmanage.get_map_address(dtype, trantype.ETHEREUM.value, False),
                  funds = stmanage.get_funds_address()
                  )
          obj.load_vlsmproof(stmanage.get_vlsmproof_address())
          [obj.append_contract(token) for token in stmanage.get_support_token_id(trantype.ETHEREUM.value)]
          obj.start()
       except Exception as e:
          parse_except(e)
       finally:
          print(f"stop: e2vm")


if __name__ == "__main__":
    main()
