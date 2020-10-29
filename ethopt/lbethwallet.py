#!/usr/bin/python3
import operator
import sys
import json
import os
sys.path.append("..")

import web3
from web3 import Web3
#"m/44'/60'/0'/0/1"


class lbethwallet:
    
    DELIMITER = ";"
    def __init__(self, mnemonic, passphrase = ""):
        self.init_account(mnemonic, passphrase)

    def split_mnemonic(self, mnemonic):
        m_i = mnemonic.split(self.DELIMITER)
        if len(m_i) == 1:
            return (m_i[0], 1)
        return (m_i[0], int(m_i[1]))

    def get_account_path(self, index):
        return f"m/44'/60'/0'/0/{index}"

    def init_account(self, mnemonic, passphrase):
        self._passphrase = passphrase
        self.accounts = []
        self._addr_map = {}
        setattr(self, "child_count", int(0))
        (self._mnemonic, num) = self.split_mnemonic(mnemonic.strip())
        web3.Account.enable_unaudited_hdwallet_features()
        for i in range(num):
            self.new_account()

        return len(self.accounts)

    def new_account(self):
        account = web3.Account.from_mnemonic(self._mnemonic, self._passphrase, self.get_account_path(self.child_count))
        self.accounts.append(account)
        self._addr_map[account.address] = self.child_count
        self.child_count += 1
        return account

    def account_count(self):
        return self.child_count

    @classmethod
    def recover(cls, filename):
        if os.path.exists(filename):
            with open(filename) as f:
                data = f.read()
                return cls(data)

    @classmethod
    def new(cls):
        account, mnemonic = web3.Account.create_with_mnemonic()
        return cls(mnemonic)

    def write_recovery(self, filename):
        with open(filename, 'wt') as f:
            f.write(self._mnemonic)
            f.write(self.DELIMITER)
            f.write(str(self.child_count))

    def get_account_by_address_or_refid(self, address_or_refid):
        id = address_or_refid
        if isinstance(address_or_refid, bytes):
            address_or_refid = address_or_refid.hex()
        if isinstance(address_or_refid, str):
            id = self._addr_map.get(address_or_refid)
        if not isinstance(id, int):
            raise Exception(f"address_or_refid({id}) type is invalid.")
        return self.accounts[id]


def main():
    #ewallet = lbethwallet("type prison nut basket borrow empower unhappy south local dish salad peace")

    ewallet = lbethwallet.recover("ethwallt_test")
    print(f"account count: {ewallet.account_count()}")
    account = ewallet.new_account()
    print(f"new account address: {account.address}")
    print(f"new account key: {account.key.hex()}")
    account = ewallet.new_account()
    print(f"new account address: {account.address}")
    print(f"new account key: {account.key.hex()}")
    print(f"account count: {ewallet.account_count()}")

    ewallet.write_recovery("ethwallt_test")

if __name__ == "__main__":
    main()
