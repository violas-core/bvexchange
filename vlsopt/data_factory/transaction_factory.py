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

def parse_events(events):
    datas = []
    if events:
        for event in events:
            datas.append({
                "key":event.key,
                "sequence_number": event.sequence_number,
                "data": {
                    "type": event.data.type,
                    "amount": {
                        "amount": event.data.amount.amount,
                        "currency": event.data.amount.currency,
                        },
                    "sender" : event.data.sender,
                    "receiver": event.data.receiver,
                    }
                })
    return datas


def parse_state(state):
    return state == "executed"

class transaction_factory(factory_base):

    global parse_state
    tran_fields = [
            field("tran_type",         "transaction.type"),
            field("script_type",       "transaction.script.type"),
            field("token_id",          "transaction.script.currency"),
            field("data",              "transaction.script.metadata"),
            field("receiver",          "transaction.script.receiver"),
            field("gas_token",         "transaction.gas_currency"),
            field("gas_unit_price",    "transaction.gas_unit_price"),
            field("max_gas_amount",    "transaction.max_gas_amount"),
            field("amount",            "transaction.script.amount"),
            field("sequence_number",   "transaction.sequence_number"),
            field("vm_status",         "vm_status.type"),
            field("state",             "vm_status.type", parse_state),
            field("gas_used",          "gas_used"),
            field("version",           "version"),
            field("events",            "events", parse_events),
            ]

    def __init__(self, data):
        factory_base.__init__(self, data)
        self.__init_show_fields()

    def __init_show_fields(self):
        global tran_fields
        self.set_fields(tran_fields)

        default_outputs = {"state": "not support",
                "events_len" : len(self.events)}

        self.extend_default_outputs(default_outputs)


    def get_version(self):
        return self.get_attr_with_path(self.get_field("version").path)

