from libra.violas_transaction import ViolasBase
from libra.bytecode import bytecodes_split

platform_address = "0"*64

class LibraMint(ViolasBase):
    def __init__(self, type, sender, payload):
        self.type = type
        self.sender = sender
        self.receiver = payload.args[0]
        self.amount = payload.args[1]
        self.sender_module_address = platform_address
        self.receiver_module_address = platform_address

class LibraP2P(ViolasBase):
    def __init__(self, type, sender, payload):
        self.type = type
        self.sender = sender
        self.receiver = payload.args[0]
        self.amount = payload.args[1]
        self.sender_module_address = platform_address
        self.receiver_module_address = platform_address

class LibraP2PWithData(ViolasBase):
    def __init__(self, type, sender, payload):
        self.type = type
        self.sender = sender
        self.receiver = payload.args[0]
        self.amount = payload.args[1]
        self.sender_module_address = platform_address
        self.receiver_module_address = platform_address
        self.data = bytes.fromhex(payload.args[2]).decode()


class LibraCreateAccount(ViolasBase):
    def __init__(self, type, sender, payload):
        self.type = type
        self.sender = sender
        self.receiver = payload.args[0]
        self.amount = payload.args[1]
        self.sender_module_address = platform_address
        self.receiver_module_address = platform_address

class LibraRotateAuthenticationKey(ViolasBase):
    def __init__(self, type, sender, payload):
        self.type = type
        self.sender = sender
        self.new_key = payload.args[0]

class ViolasPublish(ViolasBase):
    def __init__(self, type, sender, payload):
        self.type = type
        self.sender = sender

class ViolasInit(ViolasBase):
    def __init__(self, type, sender, payload):
        self.type = type
        self.sender = sender
        self.receiver = self.sender
        l = len(bytecodes_split[type][0])
        self.sender_module_address = payload.code[l: l+64]

class ViolasMint(ViolasBase):
    def __init__(self, type, sender, payload):
        self.type = type
        self.sender = sender
        self.receiver = payload.args[0]
        self.amount = payload.args[1]
        l = len(bytecodes_split[type][0])
        self.sender_module_address = payload.code[l: l+64]
        self.receiver_module_address = payload.code[l: l+64]

class ViolasP2P(ViolasBase):
    def __init__(self, type, sender, payload):
        self.type = type
        self.sender = sender
        self.receiver = payload.args[0]
        self.amount = payload.args[1]
        l = len(bytecodes_split[type][0])
        self.sender_module_address = payload.code[l: l+64]
        self.receiver_module_address = payload.code[l: l+64]

class ViolasOrder(ViolasBase):
    def __init__(self, type, sender, payload):
        self.type = type
        self.sender = sender
        self.amount = payload.args[0]
        self.price = payload.args[1]
        self.flag = payload.args[2]
        l = len(bytecodes_split[type][0])
        if self.flag == 0:
            self.sender_module_address = payload.code[l: l+64]
            self.receiver_module_address = platform_address
        else:
            self.sender_module_address = platform_address
            self.receiver_module_address = payload.code[l: l+64]

class ViolasPick(ViolasBase):
    def __init__(self, type, sender, payload):
        self.type = type
        self.sender = sender
        self.receiver = payload.args[0]
        l = len(bytecodes_split[type][0])
        self.amount = payload.args[1]
        self.price = payload.args[2]
        self.flag = payload.args[3]
        if self.flag == 0:
            self.sender_module_address = platform_address
            self.receiver_module_address = payload.code[l: l+64]
        else:
            self.sender_module_address = payload.code[l: l+64]
            self.receiver_module_address = platform_address

class ViolasWithdrawal(ViolasBase):
    def __init__(self, type, sender, payload):
        self.type = type
        self.sender = sender
        l = len(bytecodes_split[type][0])
        self.sender_module_address = payload.code[l: l+64]
        self.receiver_module_address = payload.code[l: l+64]

class ViolasInitWithData(ViolasBase):
    def __init__(self, t, sender, payload):
        self.type = t
        self.sender = sender
        l = len(bytecodes_split[t][0])
        self.sender_module_address = payload.code[l: l+64]
        self.data = bytes.fromhex(payload.args[0]).decode()


class ViolasP2PWithData(ViolasBase):
    def __init__(self, type, sender, payload):
        self.type = type
        self.sender = sender
        self.receiver = payload.args[0]
        self.amount = payload.args[1]
        l = len(bytecodes_split[type][0])
        self.sender_module_address = payload.code[l: l + 64]
        self.receiver_module_address = payload.code[l: l + 64]
        self.data = bytes.fromhex(payload.args[2]).decode()


class UnkownTransaction(ViolasBase):
    def __init__(self,  sender):
        self.type = "unknown transaction"
        self.sender = sender

class ViolasWriteSet(ViolasBase):
    def __init__(self, type, sender, payload):
        self.type = type
        self.sender = sender


type_mapping = {
    "mint": LibraMint,
    "peer_to_peer_transfer": LibraP2P,
    "peer_to_peer_transfer_with_data": LibraP2PWithData,
    "create_account": LibraCreateAccount,
    "rotate_authentication_key": LibraRotateAuthenticationKey,
    "violas_module": ViolasPublish,
    "violas_init": ViolasInit,
    "violas_mint": ViolasMint,
    "violas_peer_to_peer_transfer": ViolasP2P,
    "violas_order": ViolasOrder,
    "violas_pick": ViolasPick,
    "violas_withdrawal": ViolasWithdrawal,
    "violas_owner_init": ViolasInitWithData,
    "violas_peer_to_peer_transfer_with_data": ViolasP2PWithData
}


def get_type(sender, payload):
    if hasattr(payload, "code"):
        type = None
        for k, v in bytecodes_split.items():
            if payload.code.startswith(v[0]):
                type = k
                break
        if type:
            return type_mapping[type](type, sender, payload)
        else:
            return UnkownTransaction(sender)
    return ViolasWriteSet("write_set", sender, payload)
