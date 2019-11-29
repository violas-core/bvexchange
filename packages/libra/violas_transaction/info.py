from canoser import  Struct
from libra.violas_transaction import ViolasBase
from libra.event import EventHandle
from libra.violas_transaction import ViolasEventHandle

class  EventInfo(Struct):
    _fields = [
        ("allinone_events", EventHandle)
    ]

class ViolasEventInfo(ViolasBase):
    def __init__(self, info: EventInfo):
        self.allinone_events = ViolasEventHandle(info.allinone_events)
