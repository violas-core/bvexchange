from libra.violas_transaction import ViolasBase
from libra.violas_resource import OwnerData

class ViolasOwnerData(ViolasBase):
    def __init__(self, data:OwnerData):
        self.data = bytes(data.data).decode()
        self.owner = self.int_list_to_hex(data.owner)
