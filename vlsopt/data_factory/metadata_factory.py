#!/usr/bin/python3
import operator
import sys
import json
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "./"))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../"))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../lbdiemsdk/src"))

from diem import (
    jsonrpc,
    )

from factory_base import (
        factory_base,
        field
        )
class metadata_factory(factory_base):

    fields = [
            field("version"),
            field("timestamp"),
            field("chain_id"),
            field("diem_version"),
            field("accumulator_root_hash"),
            field("dual_attestation_limit"),
            field("script_hash_allow_list", callback = factory_base.parse_list),
            field("module_publishing_allowed"),
            ]
    def __init__(self, data):
        factory_base.__init__(self, data)
        self.__init_show_fields()
    
    def __init_show_fields(self):
        self.set_fields(self.fields)

        default_outputs = {"state": True}

        self.extend_default_outputs(default_outputs)

