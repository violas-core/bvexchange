from libra.transaction import Script
from libra.violas_transaction import ViolasBase

class ViolasScript(ViolasBase):
    def __init__(self, script: Script):
        self.code = self.int_list_to_hex(script.code)
        self.args = [ self.int_list_to_hex(arg.value) if isinstance(arg.value, list) else arg.value for arg in script.args]

