from libra.transaction import Module
from libra.violas_transaction import ViolasBase

class ViolasModule(ViolasBase):
    def __init__(self, module: Module):
        self.code = self.int_list_to_hex(module.code)
