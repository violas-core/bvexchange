from libra.transaction import Transaction
from libra.violas_transaction import ViolasSignedTransaction, ViolasBlockMetadata, ViolasWriteSet

class ViolasTransaction():
    @staticmethod
    def parse(transaction: Transaction, info, events):
        (ViolasSignedTransaction, ViolasWriteSet, ViolasBlockMetadata)[transaction.index](transaction.value, info, events)


