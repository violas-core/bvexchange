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
        factory_base
        )
class transaction_factory(factory_base):

    class field:
        def __init__(self, name, path, callback = None):
            self.name = name
            self.path = path
            self.callback = callback

        def parse(self, value):
            if self.callback:
                return self.callback(value)
            return value

    def __init__(self, data):
        factory_base.__init__(self, data)
        self.__init_show_fields()

    def __init_show_fields(self):
        self.__tran_fields = [
                self.field("tran_type",         "transaction.type"),
                self.field("script_type",       "transaction.script.type"),
                self.field("token_id",          "transaction.script.currency"),
                self.field("data",              "transaction.script.metadata"),
                self.field("receiver",          "transaction.script.receiver"),
                self.field("gas_token",         "transaction.gas_currency"),
                self.field("gas_unit_price",    "transaction.gas_unit_price"),
                self.field("max_gas_amount",    "transaction.max_gas_amount"),
                self.field("amount",            "transaction.script.amount"),
                self.field("sequence_number",   "transaction.sequence_number"),
                self.field("vm_status",         "vm_status.type"),
                self.field("state",             "vm_status.type", self.parse_state),
                self.field("gas_used",          "gas_used"),
                self.field("version",           "version"),
                self.field("events",            "events", self.parse_events),
                ]
        self.__default_output = {"state": "not support"}
        self.__default_output.update({"events_len" : len(self.events)})
        #self.__default_output.update({"events" : str(self.events)})
        

    def append_fields(self, key, path, callback = None):
        self.__tran_fields.append(self.field(key , path, callback))

    @staticmethod
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


    @staticmethod
    def parse_state(state):
        return state == "executed"

    def to_json(self):
        output = dict(self.__default_output)
        tran_datas = {field.name: field.parse(self.get_attr_with_path(field.path)) for field in self.__tran_fields}
        events = list(self.events)
        output.update(tran_datas)
        return output

        
    def get_field(self, name):
        return self.__tran_fields[name]

    def get_version(self):
        return self.get_attr_with_path(self.get_field("version").path)

