#!/usr/bin/python3
import operator
import sys
import json
import os

class proxybase():

    ASSIGNMENT = "="
    wallet_dd_map = {}
    dd_wallet_map = {}

    @classmethod
    def load(self, filename):
        if os.path.isfile(filename):
            self.__wallet_name = filename
            with open(filename) as lines:
                infos = lines.readlines()
                for info in infos:
                    return self.loads(info)
    @classmethod
    def append_address_map(self, address, dd_address):
        self.dd_wallet_map.update({dd_address:address})
        self.wallet_dd_map.update({address:dd_address})

    @classmethod
    def map_to_wallet_address(self, dd_address):
        address = self.dd_wallet_map.get(dd_address)
        return address if address else dd_address
        
    @classmethod
    def map_to_dd_address(self, address):
        dd_address = self.wallet_dd_map.get(address)
        return dd_address if dd_address else address

    @classmethod
    def loads(cls, data):
        mnemonic_num = data.split(cls.DELIMITER)
        if len(mnemonic_num) < 2 or not mnemonic_num[1].isdecimal():
            raise Exception(f"Format error: Wallet must <MNEMONIC_NUM>{cls.DELIMITER}<NUM>[ADDRESS{cls.ASSIGNMENT}DD_ADDRESS;ADDRESS{cls.ASSIGNMENT}DD_ADDRESS]")
        
        wallet = cls.new_from_mnemonic(mnemonic_num[0]) 
        wallet.generate_addresses(int(mnemonic_num[1]))
        if len(mnemonic_num) > 2:
            i = 2
            while i < len(mnemonic_num):
                address_dd = [value.strip() for value in mnemonic_num[i].split(cls.ASSIGNMENT)]
                if len(address_dd) != 2:
                    raise Exception(f"address mapping format error: ADDRESS{cls.ASSIGNMENT}DD_ADDRESS")
                
                if len(address_dd[0]) not in cls.ADDRESS_LEN or \
                        len(address_dd[1]) not in cls.ADDRESS_LEN:
                        raise Exception(f"address is invalid. {mnemonic_num[i]}")
                wallet.replace_address(address_dd[0], address_dd[1])
                wallet.append_address_map(address_dd[0], address_dd[1])

                i = i + 1

        print(wallet.name)
        return wallet

