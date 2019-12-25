from libra.transaction import SignedTransaction
from libra.violas_transaction import ViolasRawTransaction
from libra.violas_transaction import ViolasBase
from libra.violas_transaction import ViolasContractEvent
from libra.violas_transaction import ViolasTransactionInfo

from canoser.util import int_list_to_hex
import json

class ViolasSignedTransaction(ViolasBase):
    def __init__(self, transaction: SignedTransaction, version=-1, info=None, events=[]):
        self.version = version
        self.raw_txn = ViolasRawTransaction(transaction.raw_txn)
        self.public_key = int_list_to_hex(transaction.public_key)
        self.signature = int_list_to_hex(transaction.signature)
        self.events = [ ViolasContractEvent(e)for e in events ]
        if info:
            self.info = ViolasTransactionInfo(info)
            self.success = info.major_status == 4001

    def get_version(self):
        return self.version

    def get_type(self):
        return self.raw_txn.type.type

    def get_sender_address(self):
        return self.raw_txn.sender

    def get_pubkey(self):
        return self.public_key

    def get_sender_sequence(self):
        return self.raw_txn.sequence_number

    def get_max_gas_amount(self):
        return self.raw_txn.max_gas_amount

    def get_gas_unit_price(self):
        return self.raw_txn.gas_unit_price

    def get_expiration_time(self):
        return self.raw_txn.expiration_time

    def get_receiver_address(self):
        return self.raw_txn.type.receiver

    def get_sender_module_address(self):
        return self.raw_txn.type.sender_module_address

    def get_receiver_module_address(self):
        return self.raw_txn.type.receiver_module_address

    def get_amount(self):
        return self.raw_txn.type.amount

    def get_info(self):
        return self.info

    def get_data(self):
        return self.raw_txn.type.data

    def get_new_key(self):
        return self.raw_txn.type.new_key

    def get_index(self):
        return 0





