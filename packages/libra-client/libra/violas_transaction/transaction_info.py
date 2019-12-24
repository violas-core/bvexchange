from libra.transaction import TransactionInfo
from libra.violas_transaction import ViolasBase


class ViolasTransactionInfo(ViolasBase):
    def __init__(self, info: TransactionInfo):
        self.transaction_hash = self.int_list_to_hex(info.transaction_hash)
        self.state_root_hash = self.int_list_to_hex(info.state_root_hash)
        self.event_root_hash = self.int_list_to_hex(info.event_root_hash)
        self.gas_used = info.gas_used
        self.major_status = info.major_status
