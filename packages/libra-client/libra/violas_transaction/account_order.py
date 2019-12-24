
from libra.violas_transaction import ViolasBase
from libra.violas_resource import ViolasOrder

class ViolasAccountOrder(ViolasBase):
    def __init__(self, order: ViolasOrder):
        self.token = order.token
        self.price = order.price