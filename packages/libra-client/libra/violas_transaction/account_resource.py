from libra.account_resource import AccountResource
from libra.violas_transaction import ViolasBase
from libra.violas_transaction import ViolasEventHandle

class ViolasAccountResource(ViolasBase):
    def __init__(self, resource: AccountResource):
        self.authentication_key = self.int_list_to_hex(resource.authentication_key)
        self.balance = resource.balance
        self.delegated_key_rotation_capability = resource.delegated_key_rotation_capability
        self.delegated_withdrawal_capability = resource.delegated_withdrawal_capability
        self.received_events = ViolasEventHandle(resource.received_events)
        self.sent_events = ViolasEventHandle(resource.sent_events)
        self.sequence_number = resource.sequence_number