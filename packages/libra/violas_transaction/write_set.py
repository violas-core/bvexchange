from libra.transaction import WriteSet
from libra.violas_transaction import ViolasBase
from libra.transaction import WriteOp
from libra.access_path import AccessPath
from canoser.util import int_list_to_hex

class ViolasWriteOp(ViolasBase):
    def __init__(self, op: WriteOp):
        self.op =  op.value if op.index == 0 else int_list_to_hex(op.value)

class ViolasAccessPath(ViolasBase):
    def __init__(self, access: AccessPath):
        self.address = int_list_to_hex(access.address)
        self.path = int_list_to_hex(access.path)

class ViolasWriteSet(ViolasBase):
    def __init__(self, write_set: WriteSet):
        self.access_path = ViolasAccessPath(write_set.write_set[0][0])
        self.write_op = ViolasWriteOp(write_set.write_set[0][1])