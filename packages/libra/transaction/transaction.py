from canoser import RustEnum
from libra.transaction.signed_transaction import SignedTransaction
from libra.transaction.write_set import WriteSet
from libra.block_metadata import BlockMetadata
from libra.hasher import gen_hasher, HashValue
from libra.key_factory import new_sha3_256


class Transaction(RustEnum):
    _enums = [
        ('UserTransaction', SignedTransaction),
        ('WriteSet', WriteSet),
        ('BlockMetadata', BlockMetadata)
    ]

    def hash(self):
        shazer = gen_hasher(b"TRANSACTION")
        shazer.update(self.serialize())
        return shazer.digest()
