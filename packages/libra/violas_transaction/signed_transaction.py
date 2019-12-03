from libra.transaction import SignedTransaction
from libra.violas_transaction import ViolasRawTransaction
from libra.violas_transaction import ViolasBase
from libra.violas_transaction import ViolasContractEvent
from libra.violas_transaction import ViolasTransactionInfo

from canoser.util import int_list_to_hex
import json

class ViolasSignedTransaction(ViolasBase):
    def __init__(self, transaction: SignedTransaction, version, info, events=[] ):
        self.version = version
        self.raw_txn = ViolasRawTransaction(transaction.raw_txn)
        self.public_key = int_list_to_hex(transaction.public_key)
        self.signature = int_list_to_hex(transaction.signature)
        self.events = [ ViolasContractEvent(e)for e in events ]
        self.info = ViolasTransactionInfo(info)
        self.success = info.major_status == 4001

    def get_version(self):
        return self.version

    def get_type(self):
        try:
            return self.raw_txn.type.type
        except:
            return None

    def get_sender_address(self):
        try:
            return self.raw_txn.sender
        except:
            return None

    def get_pubkey(self):
        try:
            return self.public_key
        except:
            return None

    def get_sender_sequence(self):
        return self.raw_txn.sequence_number

    def get_max_gas_amount(self):
        return self.raw_txn.max_gas_amount

    def get_gas_unit_price(self):
        return self.raw_txn.gas_unit_price

    def get_expiration_time(self):
        return self.raw_txn.expiration_time

    def get_receiver_address(self):
        try:
            return self.raw_txn.type.receiver
        except:
            return None

    def get_sender_module_address(self):
        try:
            return self.raw_txn.type.sender_module_address
        except:
            return None

    def get_receiver_module_address(self):
        try:
            return self.raw_txn.type.receiver_module_address
        except:
            return None

    def get_amount(self):
        try:
            return self.raw_txn.type.amount
        except:
            return None

    def get_info(self):
        try:
            return self.info
        except:
            return None

    def get_data(self):
        try:
            return json.loads(self.raw_txn.type.data)
        except:
            return None

    def get_data_str(self):
        try:
            return self.raw_txn.type.data
        except:
            return None

    def get_new_key(self):
        try:
            return self.raw_txn.type.new_key
        except:
            return None




