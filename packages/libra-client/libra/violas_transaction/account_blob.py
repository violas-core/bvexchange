from libra.account_resource import AccountStateBlob
from libra.account_resource import AccountState
from libra.violas_transaction import ViolasAccountState
from libra.violas_transaction import ViolasBase

class ViolasAccountBlob(ViolasBase):
    def __init__(self, blob: AccountStateBlob, version):
        self.blob = ViolasAccountState(AccountState.deserialize(blob.blob))
        self.version = version