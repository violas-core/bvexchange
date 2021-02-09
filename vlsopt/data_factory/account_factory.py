#!/usr/bin/python3
import operator
import sys
import json
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "./"))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../"))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../lbdiemsdk/src"))


from diem import (
    jsonrpc,
    )

from factory_base import (
        factory_base
        )
class account_factory(factory_base):

    def __init__(self, data):
        factory_base.__init__(self, data)

    def is_published(self, token_id):
        for balance in self.__data.balances:
            if token_id == balance.currency:
                return True
        return False

    def get_role_id(self):
        role_id = self.role.type
        if role_id == jsonrpc.ACCOUNT_ROLE_CHILD_VASP:
            return 6
        elif role_id == jsonrpc.ACCOUNT_ROLE_PARENT_VASP:
            return 5
        elif role_id == jsonrpc.ACCOUNT_ROLE_DESIGNATED_DEALER:
            return 2
        elif role_id == jsonrpc.ACCOUNT_ROLE_UNKNOWN:
            return sys.maxsize

        raise Exception(f"no-match role for {role_id}")

