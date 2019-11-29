from canoser import Struct, Uint8, bytes_to_int_list, hex_to_int_list
from libra.transaction.transaction_argument import TransactionArgument, normalize_public_key
from libra.bytecode import bytecodes
from libra.account_address import Address
from canoser.util import int_list_to_hex, bytes_to_hex
from libra.bytecode import default_module_address


class Script(Struct):
    _fields = [
        ('code', [Uint8]),
        ('args', [TransactionArgument])
    ]

    @classmethod
    def gen_transfer_script(cls, receiver_address,micro_libra):
        receiver_address = Address.normalize_to_int_list(receiver_address)
        code = bytecodes["peer_to_peer_transfer"]
        args = [
                TransactionArgument('Address', receiver_address),
                TransactionArgument('U64', micro_libra)
            ]
        return Script(code, args)

    @classmethod
    def gen_mint_script(cls, receiver_address,micro_libra):
        receiver_address = Address.normalize_to_int_list(receiver_address)
        code = bytecodes["mint"]
        args = [
                TransactionArgument('Address', receiver_address),
                TransactionArgument('U64', micro_libra)
            ]
        return Script(code, args)

    @classmethod
    def gen_create_account_script(cls, fresh_address):
        fresh_address = Address.normalize_to_int_list(fresh_address)
        code = bytecodes["create_account"]
        args = [
                TransactionArgument('Address', fresh_address),
                TransactionArgument('U64', 0)
            ]
        return Script(code, args)

    @classmethod
    def gen_rotate_auth_key_script(cls, public_key):
        key = normalize_public_key(public_key)
        code = bytecodes["rotate_authentication_key"]
        args = [
                TransactionArgument('ByteArray', key)
            ]
        return Script(code, args)

    @staticmethod
    def get_script_bytecode(script_name):
        return bytecodes[script_name]



    @classmethod
    def gen_violas_init_script(cls,module_address):
        if isinstance(module_address, bytes):
            module_address = bytes_to_hex(module_address)

        code = hex_to_int_list(int_list_to_hex(bytecodes["violas_init"]).replace(
            default_module_address, module_address))
        args = [
        ]
        return Script(code, args)

    @classmethod
    def gen_violas_mint_script(cls, receiver_address,micro_libra,module_address):
        receiver_address = Address.normalize_to_int_list(receiver_address)
        if isinstance(module_address, bytes):
            module_address = bytes_to_hex(module_address)

        code = hex_to_int_list(int_list_to_hex(bytecodes["violas_mint"]).replace(default_module_address, module_address))
        args = [
                TransactionArgument('Address', receiver_address),
                TransactionArgument('U64', micro_libra)
            ]
        return Script(code, args)

    @classmethod
    def gen_violas_transfer_script(cls, receiver_address, micro_libra, module_address):
        receiver_address = Address.normalize_to_int_list(receiver_address)
        if isinstance(module_address, bytes):
            module_address = module_address.hex()
        code = hex_to_int_list(int_list_to_hex(bytecodes["violas_peer_to_peer_transfer"]).replace(default_module_address, module_address))
        args = [
                TransactionArgument('Address', receiver_address),
                TransactionArgument('U64', micro_libra)
            ]
        return Script(code, args)

    @classmethod
    def gen_violas_order_script(cls, module_address, order_amount, pick_amount, flag):
        if isinstance(module_address, bytes):
            module_address = module_address.hex()
        code = hex_to_int_list(int_list_to_hex(bytecodes["violas_order"]).replace(default_module_address, module_address))
        args = [
                TransactionArgument('U64', order_amount),
                TransactionArgument('U64', pick_amount),
                TransactionArgument('U64', flag)
            ]
        return Script(code, args)

    @classmethod
    def gen_violas_pick_script(cls, module_address, order_address, order_amount, pick_amount, flag):
        if isinstance(module_address, bytes):
            module_address = module_address.hex()
        order_address = Address.normalize_to_int_list(order_address)
        code = hex_to_int_list(int_list_to_hex(bytecodes["violas_pick"]).replace(default_module_address, module_address))
        args = [
                TransactionArgument('Address', order_address),
                TransactionArgument('U64', order_amount),
                TransactionArgument('U64', pick_amount),
                TransactionArgument('U64', flag)
        ]
        return Script(code, args)

    @classmethod
    def gen_violas_withdrawal_script(cls, module_address):
        if isinstance(module_address, bytes):
            module_address = module_address.hex()
        code = hex_to_int_list(int_list_to_hex(bytecodes["violas_withdrawal"]).replace(default_module_address, module_address))
        flag = 1 if module_address == bytes([0]*32) else 0
        args = [
            TransactionArgument('U64', flag)
        ]
        return Script(code, args)

    @classmethod
    def gen_violas_owner_init_script(cls, module_address, mesg):
        if isinstance(mesg, str):
            mesg = bytes(mesg, encoding="utf8")
        if isinstance(module_address, bytes):
            module_address = module_address.hex()
        code = hex_to_int_list(int_list_to_hex(bytecodes["violas_owner_init"]).replace(default_module_address, module_address))
        args = [
            TransactionArgument('ByteArray', bytes_to_int_list(mesg))
        ]
        return Script(code, args)

    @classmethod
    def gen_violas_peer_to_peer_transfer_with_data_script(cls, receiver_address, micro_libra, module_address, mesg):
        if isinstance(mesg, str):
            mesg = bytes(mesg, encoding="utf8")
        receiver_address = Address.normalize_to_int_list(receiver_address)
        if isinstance(module_address, bytes):
            module_address = module_address.hex()
        code = hex_to_int_list(int_list_to_hex(bytecodes["violas_peer_to_peer_transfer_with_data"]).replace(default_module_address, module_address))
        args = [
                TransactionArgument('Address', receiver_address),
                TransactionArgument('U64', micro_libra),
                TransactionArgument('ByteArray', bytes_to_int_list(mesg))
            ]
        return Script(code, args)

