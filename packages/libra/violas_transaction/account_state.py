from libra.account_resource import AccountState
from libra.account_resource import AccountResource
from libra.violas_transaction import ViolasBase
from libra.account_resource import AccountConfig
from libra.violas_transaction import ViolasAccountResource
from libra.violas_transaction import EventInfo, ViolasEventInfo
from libra.violas_resource import ViolasResource, ViolasInfo, ViolasOwnerData, ViolasOrder, ViolasOrder2
from libra.violas_transaction import ViolasAccountOrder

class ViolasAccountState(ViolasBase):
    def __init__(self, state:AccountState):
        self.violas_resource = {}
        mmaps = state.ordered_map
        value = mmaps.get(AccountConfig.account_resource_path())
        if value:
            self.account_resource = ViolasAccountResource(AccountResource.deserialize(value))
            mmaps.pop(AccountConfig.account_resource_path())

        for key, value in mmaps.items():
            if key.hex().startswith("00"):
                self.module_code = self.int_list_to_hex(value)
                mmaps.pop(key)
                break

        addrs = {}
        for key, value in mmaps.items():
            if 32 == len(value):
                addrs[key] = value

        for key in addrs.keys():
            mmaps.pop(key)

        useds = []
        for addr in addrs.values():
            addr = self.int_list_to_hex(addr)
            self.violas_resource[addr] = {}
            balance_key = ViolasResource.violas_resource_path(addr)
            if mmaps.get(balance_key):
                useds.append(balance_key)
                self.violas_resource[addr]["balance"]= int.from_bytes(bytes(mmaps[balance_key]), byteorder="little", signed=False)
            info_key = ViolasInfo.violas_info_path(addr)
            if mmaps.get(info_key):
                useds.append(info_key)
                self.violas_resource[addr]["info"] = ViolasEventInfo(EventInfo.deserialize(mmaps[info_key]))
            owner_key = ViolasOwnerData.violas_ownerdata_path(addr)
            if mmaps.get(owner_key):
                useds.append(owner_key)
                self.violas_resource["tender"] = bytes(ViolasOwnerData.deserialize(mmaps.get(owner_key)).data).decode()
            order_key = ViolasOrder.violas_order_path(addr)
            if mmaps.get(order_key):
                useds.append(order_key)
                self.violas_resource[addr]["vstable"] = ViolasAccountOrder(ViolasOrder.deserialize(mmaps.get(order_key)))
            order_key = ViolasOrder2.violas_order_path(addr)
            if mmaps.get(order_key):
                useds.append(order_key)
                self.violas_resource[addr]["vtoken"] = ViolasAccountOrder(ViolasOrder2.deserialize(mmaps.get(order_key)))

        for used in useds:
            mmaps.pop(used)

        if len(mmaps):
            self.Unused = {}

        for k, v in mmaps.items():
            k = k.hex()
            if len(v) == 8:
                self.Unused[k] = int.from_bytes(bytes(v), byteorder="little", signed=False)
            else:
                self.Unused[k] = self.int_list_to_hex(v)

    def violas_get_info(self):
        try:
            return self.violas_resource
        except:
            return None

    def violas_get_tender_name(self):
        try:
            return self.violas_resource["tender"]
        except:
            return None

    def violas_get_address_info(self, address):
        if isinstance(address, bytes):
            address = address.hex()
        try:
            return self.violas_resource[address]
        except:
            return None

    def violas_get_balance(self, module_address):
        if isinstance(module_address, bytes):
            module_address = module_address.hex()
        try:
            return self.violas_resource[module_address]["balance"]
        except:
            return 0

    def violas_get_order(self, module_address, source_is_vtoken):
        if isinstance(module_address, bytes):
            module_address = module_address.hex()
        try:
            if source_is_vtoken:
                return self.violas_resource[module_address]["vtoken"]
            else:
                return self.violas_resource[module_address]["vstable"]
        except:
            return None

    def has_module(self):
        return hasattr(self, "module_code")

    def get_balance(self):
        try:
            return self.account_resource.balance
        except:
            return 0




