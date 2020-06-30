#!/usr/bin/python3
from setting import setting
import comm.values
from comm import result
from comm.result import parse_except
from comm.functions import get_address_from_full_address 
from comm.functions import json_print

VIOLAS_ADDRESS_LEN = comm.values.VIOLAS_ADDRESS_LEN

def check_setting():
    pass

def set_conf_env_default():
    setting.set_conf_env_default()

def set_conf_env(conffile):
    setting.set_conf_env(conffile)

def get_conf_env():
    return setting.get_conf_env()

def get_looping_sleep(mtype):
    try:
        sleep = setting.looping_sleep.get(mtype, 1)
    except Exception as e:
        sleep = 1
    return sleep

def __get_address_list(atype, mtype, chain = None, full = True):
    try:
        addresses =  [dict.get("address") for dict in setting.address_list.get(atype) \
                if dict["type"] == mtype and mtype is not None and (chain is None or dict["chain"] == chain)]
        if addresses is not None and len(addresses) > 0:
            if full:
                return addresses
            else:
                min_len = min(VIOLAS_ADDRESS_LEN)
                assert min_len > 0 , "address min(VIOLAS_ADDRESS_LEN) is invalid."
                return [get_address_from_full_address(addr) for addr in addresses]
    except Exception as e:
        parse_except(e)
    return None

#maybe use. so keep it until libra support usd eur ...
#def __get_tokenid_list(atype, mtype, chain = None):
#    try:
#        return [dict.get("tokenid") for dict in setting.address_list.get(atype) \
#                if dict["type"] == mtype and mtype is not None and (chain is None or dict["chain"] == chain)]
#    except Exception as e:
#        parse_except(e)
#    return None
#
def get_receiver_address_list(mtype, chain = None, full = True):
    try:
        return __get_address_list("receiver", mtype, chain, full)
    except Exception as e:
        parse_except(e)
    return None

def get_sender_address_list(mtype, chain = None, full = True):
    try:
        return __get_address_list("sender", mtype, chain, full)
    except Exception as e:
        parse_except(e)
    return None

#maybe use. so keep it until libra support usd eur ...
#def get_token_address(mtype, chain = None, full = True):
#    try:
#        ms = __get_address_list("token", mtype, chain, full)
#        if ms is None or len(ms) == 0:
#            return None
#        assert len(ms) == 1, f"token type({mtype}) chain({chain}) found multi coins found, check it"
#        return ms[0]
#    except Exception as e:
#        parse_except(e)
#    return None

def get_combine_address(mtype = "b2v", chain = "btc", full = True):
    try:
        ms = __get_address_list("combine", mtype, chain, full)
        if ms is None or len(ms) == 0:
            return None
        assert len(ms) == 1, f"({mtype}) chain({chain}) found multi combin address , check it"
        return ms[0]
    except Exception as e:
        parse_except(e)
    return None

#maybe use. so keep it until libra support usd eur ...
#def get_token_id(mtype = "b2v", chain = "btc"):
#    try:
#        ms = __get_tokenid_list("token", mtype, chain)
#        if ms is None or len(ms) == 0:
#            return None
#        assert len(ms) == 1, f"({mtype}) chain({chain}) found multi token id({ms}), check it"
#        return ms[0]
#    except Exception as e:
#        parse_except(e)
#    return None
#

def get_db(mtype):
    try:
        dbs = [dict for dict in setting.db_list if dict.get("db") == mtype and mtype is not None]
        if dbs is not None and len(dbs) > 0:
            return dbs[0]
    except Exception as e:
        parse_except(e)
    return None


def get_libra_nodes():
    try:
        return setting.libra_nodes
    except Exception as e:
        parse_except(e)
    return None

def get_violas_servers():
    try:
        return setting.violas_servers
    except Exception as e:
        parse_except(e)
    return None

def get_violas_nodes():
    try:
        return setting.violas_nodes
    except Exception as e:
        parse_except(e)
    return None

def get_btc_conn():
    try:
        return setting.btc_conn
    except Exception as e:
        parse_except(e)
    return None

def get_traceback_limit():
    try:
        return setting.traceback_limit
    except Exception as e:
        parse_except(e)
    return 0

def get_db_echo():
    try:
        return setting.db_echo
    except Exception as e:
        parse_except(e)
    return None

def get_max_times(mtype):
    try:
        return setting.v2b_maxtimes
    except Exception as e:
        parse_except(e)
    return 0

def get_token_map(token = None):
    try:
        if token:
            return setting.token_map.get(token)
        return setting.token_map
    except Exception as e:
        parse_except(e)
    return None

def get_type_token_map(mtype = None):
    try:
        if mtype:
            return setting.type_token_map.get(mtype)
        return setting.type_token_map
    except Exception as e:
        parse_except(e)
    return None

def get_support_token_id(chain = None):
    try:
        if chain:
            return setting.support_token_id.get(chain)
        return setting.support_token_id
    except Exception as e:
        parse_except(e)
    return None

def get_conf():
    infos = {}
    mtypes = ["v2b", "v2l", "l2v", "b2v", "vfilter", "lfilter"]
    for mtype in mtypes:
        info = {}
        info["receiver"] = get_receiver_address_list(mtype)
        info["sender"] = get_sender_address_list(mtype)
        info["module"] = get_module_address(mtype, 'violas')
        info["db"] = get_db(mtype)
        if info["db"] is not None:
            info["db"]["password"] = "password is keep secret"
        info["loop sleep"] = get_looping_sleep(mtype)
        info["max times"] = get_max_times(mtype)
        info["combine"] = get_combine_address(mtype)
        infos[mtype] = info
    infos["traceback limit"] = get_traceback_limit()
    infos["btc conn"] = get_btc_conn()
    infos["violas nodes"] = get_violas_nodes()
    infos["violas server"] = get_violas_servers()
    infos["libra nodes"] = get_libra_nodes()
    return infos


def main():
    set_conf_env("bvexchange.toml")
    mtypes = ["v2b", "v2l", "l2v", "b2v", "vfilter", "lfilter"]

    for mtype in mtypes:
        print(f"receiver address({mtype}): {get_receiver_address_list(mtype)}")
        print(f"sender address({mtype}): {get_sender_address_list(mtype)}")
        print(f"module address({mtype}): {get_module_address(mtype, 'violas')}")
        print(f"get db({mtype}): {get_db(mtype)}")
        print(f"get looping sleep({mtype}):{get_looping_sleep(mtype)}")
        print(f"get max times({mtype})):{get_max_times(mtype)}")
        print(f"combin address({mtype}): {get_combine_address(mtype)}")

    print(f"get traceback limit: {get_traceback_limit()}")
    print(f"get btc_node: {get_btc_conn()}")
    print(f"get violas nodes: {get_violas_nodes()}")
    print(f"get violas_servers: {get_violas_servers()}")
    print(f"get libra nodes: {get_libra_nodes()}")
    print(f"get db echo :{get_db_echo()}")
    print(f"get token_map: ")
    json_print(get_token_map())
    print(f"get token_map(USD): {get_token_map('USD')}")
    print(f"get type_token_map: ")
    json_print(get_type_token_map())
    print(f"get type_token_map(l2vusd): {get_type_token_map('l2vusd')}")
    json_print(get_support_token_id())
    print(f"get support_token_id(libra): {get_support_token_id('libra')}")
    print(f"get support_token_id(violas): {get_support_token_id('violas')}")

    #json_print(get_conf())

if __name__ == "__main__":
    main()
