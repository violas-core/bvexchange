from libra.transaction import Program
from libra.violas_transaction import ViolasBase
from libra.transaction import TransactionArgument

class ViolasProgram(ViolasBase):
    def __init__(self, program: Program):
        self.code = self.int_list_to_hex(program.code)
        self.modules = self.int_list_to_hex(program.modules)
        self.args = [ self.int_list_to_hex(arg.value) if isinstance(arg.value, list) else arg.value for arg in program.args]