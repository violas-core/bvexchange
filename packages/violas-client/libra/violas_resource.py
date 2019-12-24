from libra.access_path import *
from libra.language_storage import StructTag
from libra.event import EventHandle
from canoser import BytesT

class ViolasResource(Struct):
    COIN_MODULE_NAME = "ViolasToken"
    COIN_STRUCT_NAME = "T"

    _fields = [
        ('violas_balance', Uint64)
    ]

    @classmethod
    def violas_resource_path(cls, address):
        return bytes(AccessPath.resource_access_vec(cls.violas_struct_tag(address),[]))

    @classmethod
    def violas_struct_tag(cls,address):
        return StructTag(
            hex_to_int_list(address),
            cls.COIN_MODULE_NAME,
            cls.COIN_STRUCT_NAME,
            []
    )

class ViolasInfo(Struct):
    COIN_MODULE_NAME = "ViolasToken"
    COIN_STRUCT_NAME = "Info"

    _fields = [
        ('magic', Uint64),
        ('token', Address),
        ('allinone_events', EventHandle)
    ]

    @classmethod
    def violas_info_path(cls,address):
        return bytes(AccessPath.resource_access_vec(cls.violas_struct_tag(address),[]))

    @classmethod
    def violas_struct_tag(cls,address):
        return StructTag(
            hex_to_int_list(address),
            cls.COIN_MODULE_NAME,
            cls.COIN_STRUCT_NAME,
            []
    )


class OwnerData(Struct):
    COIN_MODULE_NAME = "ViolasToken"
    COIN_STRUCT_NAME = "OwnerData"

    _fields = [
        ('data', [Uint8]),
        ('owner', Address),
        ('bulletins', BytesT)
    ]

    @classmethod
    def violas_ownerdata_path(cls,address):
        return bytes(AccessPath.resource_access_vec(cls.violas_struct_tag(address),[]))

    @classmethod
    def violas_struct_tag(cls,address):
        return StructTag(
            hex_to_int_list(address),
            cls.COIN_MODULE_NAME,
            cls.COIN_STRUCT_NAME,
            []
    )

class ViolasOrder(Struct):
    COIN_MODULE_NAME = "ViolasToken"
    COIN_STRUCT_NAME = "Order"

    _fields = [
        ('token', Uint64),
        ('price', Uint64)
    ]


    @classmethod
    def violas_order_path(cls,address):
        return bytes(AccessPath.resource_access_vec(cls.violas_struct_tag(address),[]))

    @classmethod
    def violas_struct_tag(cls,address):
        return StructTag(
            hex_to_int_list(address),
            cls.COIN_MODULE_NAME,
            cls.COIN_STRUCT_NAME,
            []
    )

class ViolasOrder2(Struct):
    COIN_MODULE_NAME = "ViolasToken"
    COIN_STRUCT_NAME = "Order2"

    _fields = [
        ('token', Uint64),
        ('price', Uint64)
    ]

    @classmethod
    def violas_order_path(cls,address):
        return bytes(AccessPath.resource_access_vec(cls.violas_struct_tag(address),[]))

    @classmethod
    def violas_struct_tag(cls,address):
        return StructTag(
            hex_to_int_list(address),
            cls.COIN_MODULE_NAME,
            cls.COIN_STRUCT_NAME,
            []
    )