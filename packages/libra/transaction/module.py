from canoser import Struct, Uint8
from libra.bytecode import bytecodes
from canoser.util import int_list_to_hex, bytes_to_hex, hex_to_int_list
from libra.bytecode import default_module_address

class Module(Struct):
    _fields = [
        ('code', [Uint8])
    ]


    @classmethod
    def gen_violas_publish_module(cls, module_address):
        if isinstance(module_address, bytes):
            module_address = bytes_to_hex(module_address)
        if isinstance(module_address, list):
            module_address = int_list_to_hex(module_address)
        code = hex_to_int_list(int_list_to_hex(bytecodes["violas_module"]).replace(
            default_module_address, module_address))
        return Module(code)
