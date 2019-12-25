from libra.event import EventHandle
from libra.violas_transaction import ViolasBase
from libra.contract_event import ContractEvent
from canoser import *
from libra.account_address import Address
from libra.language_storage import StructTag

from libra.account_config import AccountEvent


class ViolasEventHandle(ViolasBase):
    def __init__(self, handle: EventHandle):
        self.count = handle.count
        self.key  = self.int_list_to_hex(handle.key)



class ViolasEventProto(Struct):
    _fields = [
        ("etype", Uint64),
        ("sender", Address),
        ("receiver", Address),
        ("token", Address),
        ("amount", Uint64),
        ("price", Uint64),
        ("data", [Uint8])
    ]

class ViolasStructTag(ViolasBase):
    def __init__(self, tag: StructTag):
        self.address = self.int_list_to_hex(tag.address)
        self.module = tag.module
        self.name = tag.name
        self.type_params = tag.type_params


class LibraEvent(ViolasBase):
    def __init__(self, event: AccountEvent):
        self.amount = event.amount
        self.account = self.int_list_to_hex(event.account)
        self.metadata = bytes(event.metadata).decode()

class ViolasEvent(ViolasBase):
    def __init__(self, event: ViolasEventProto):
        self.etype = event.etype
        self.sender = self.int_list_to_hex(event.sender)
        self.receiver = self.int_list_to_hex(event.receiver)
        self.token = self.int_list_to_hex(event.token)
        self.amount = event.amount
        self.price = event.price
        self.data = bytes(event.data).decode()


class ViolasContractEvent(ViolasBase):
    def __init__(self, event: ContractEvent, transaction_version=None, event_index=None):
        self.key = self.int_list_to_hex(event.key)
        self.sequence_number = event.event_seq_num
        if(event.type_tag.index == 4):
            self.tag = ViolasStructTag(event.type_tag.value)
        elif(event.type_tag.index in (2, 3)):
            self.tag = self.int_list_to_hex(event.type_tag.value)
        else:
            self.tag = self.event.type_tag.value

        try:
            if self.tag.module == "LibraAccount":
                self.event = LibraEvent(AccountEvent.deserialize(event.event_data))
            elif self.tag.module == "ViolasToken":
                self.event = ViolasEvent(ViolasEventProto.deserialize(event.event_data))
            else:
                print("unknown event")
        except:
            print("known event with unkonwn data")

        if transaction_version:
            self.transaction_version = transaction_version
        if event_index:
            self.event_index = event_index

    def is_libra_event(self):
        return isinstance(self.event, LibraEvent)

    def is_violas_event(self):
        return isinstance(self.event, ViolasEvent)

    def get_key(self):
        return self.key

    def get_sequence_number(self):
        return self.sequence_number

    def get_moudle(self):
        if isinstance(self.tag, ViolasStructTag):
            return self.tag.module

    def get_name(self):
        if isinstance(self.tag, ViolasStructTag):
            return self.tag.name

    def get_module_address(self):
        if isinstance(self.tag, ViolasStructTag):
            return self.tag.address
