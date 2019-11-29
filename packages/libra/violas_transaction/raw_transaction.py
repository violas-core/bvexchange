from libra.transaction import RawTransaction
from libra.violas_transaction import ViolasBase
from libra.violas_transaction import get_type
from libra.violas_transaction import ViolasProgram, ViolasWriteSet, ViolasScript, ViolasModule

class ViolasRawTransaction(ViolasBase):
    def __init__(self, raw_transaction: RawTransaction):
        self.sender = self.int_list_to_hex(raw_transaction.sender)
        self.sequence_number = raw_transaction.sequence_number
        self.payload = (ViolasProgram, ViolasWriteSet, ViolasScript, ViolasModule)[raw_transaction.payload.index](raw_transaction.payload.value)
        self.max_gas_amount = raw_transaction.max_gas_amount
        self.gas_unit_price = raw_transaction.gas_unit_price
        self.expiration_time = raw_transaction.expiration_time
        self.type = get_type(self.sender, self.payload)

