from canoser import  Struct, Uint64
from libra.account_address import Address
from libra.violas_transaction import ViolasBase

class AllInOneEvent(Struct):
    _fields = [
        ("etype", Uint64),
        ("sender", Address),
        ("receiver", Address),
        ("token", Address),
        ("amount", Uint64),
        ("price", Uint64)
    ]

class ViolasAllInOneEvent(ViolasBase):
    def __init__(self, event: AllInOneEvent):
        self.etype = event.etype
        self.sender = event.sender
        self.receiver = event.receiver
        self.token = event.token
        self.amount = event.amount
        self.price = event.price