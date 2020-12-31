#!/usr/bin/python3
import sys, getopt, os
import json
sys.path.append(os.getcwd())
sys.path.append("..")
import setting as config_setting

_default_value = {}
class dataproof():
    ADDRS_SPLIT = ","
    FIELD_SPLIT = ":"

    def __init__(self):
        pass

    def set_default_value(self, key, value):
        _default_value.update({key:value})

    def get_default_value(self, key):
        return _default_value.get(key)

    def set_config(self, key, value):
        config_setting.setting.set(key, value)

    def get_config(self, key):
        default = self.get_default_value(key)
        return config_setting.setting.get(key, default)

    def default_values(self):
        return _default_value

    @property
    def datas(self):
        datas = {}
        datas.update(_default_value)
        datas.update(config_setting.setting.datas)
        return datas

class walletdatas(dataproof):
    def __init__(self):
        dataproof.__init__(self)
        self.__init_defalut()

    def __init_defalut(self):
        self.__init_wallet_info()

    def __wallet_key(self, chain):
        return f"{chain}_wallet"

    def __init_wallet_info(self):
        self.set_default_value(f"{self.__wallet_key('violas')}", "vwallet")
        self.set_default_value(f"{self.__wallet_key('libra')}", "vwallet")
        self.set_default_value(f"{self.__wallet_key('btc')}", "bwallet")
        self.set_default_value(f"{self.__wallet_key('ethereum')}", "ewallet")

    def get_wallet(self, chain):
        key = self.__wallet_key(chain)
        return self.get_config(key)

    def update_wallet(self, chain, data):
        key = self.__wallet_key(chain)
        if chain.lower() == "btc":
            #set for address:privkey
            if data.find(self.ADDRS_SPLIT) > 0 or data.find(self.FIELD_SPLIT) > 0:
                datas = {}
                addrs = data.split(self.ADDRS_SPLIT)
                assert len(addrs) > 0, f"data({data}) format is invalid."
                for addr in addrs:
                    fields = addr.split(self.FIELD_SPLIT)
                    assert len(fields) == 2, f"{addr} format is invalid, format: <ADDRESS>:<PRIVKEY>"
                    datas.update({fields[0]:{"address":fields[0], "publickey":None, "privkey": fields[1]}})
                return self.set_update(key, datas)
                
        return self.set_config(key, data)

    def __call__(self, *args, **kwargs):
        return self.get_wallet(args[0])


class configdatas(dataproof):
    def __init__(self):
        dataproof.__init__(self)
        self.__init_default()

    def __init_default(self):
        self.set_default_value("eth_usd_chain", False)
        self.set_default_value("retry_maxtimes", sys.maxsize)
        self.set_default_value("exchange_async", True)

    def __getattr__(self, name):
        print(f"{name}----")
        if name == "setting":
            return config_setting.setting

    def __call__(self, *args, **kwargs):
        key = args[0]
        return self.get_config(key)


class settingproxy(configdatas):
    def __init__(self):
        configdatas.__init__(self)

    def __getattr__(self, name):
        if name == "setting":
            return config_setting.setting

    def __call__(self, *args, **kwargs):
        key = args[0]
        return self.get_config(key)

wallets = walletdatas()
configs = configdatas()
setting = settingproxy()

if __name__ == "__main__":
    setting.setting.set_conf_env("../bvexchange.toml")
    print(wallets("violas"))
    print(configs("violas_wallet"))
    print(setting.setting.get_conf_env())
