from libra.violas_transaction import ViolasBase
from libra.violas_transaction import ViolasEventHandle
from libra.violas_resource import ViolasInfo


class ViolasEventInfo(ViolasBase):
    def __init__(self, info: ViolasInfo):
        self.magic = info.magic
        self.token = self.int_list_to_hex(info.token)
        self.allinone_events = ViolasEventHandle(info.allinone_events)
