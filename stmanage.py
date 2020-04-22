#!/usr/bin/python3
import setting
import comm.values
from comm import result
from comm.result import parse_except
 

VIOLAS_ADDRESS_LEN = comm.values.VIOLAS_ADDRESS_LEN
def check_setting():
    pass

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
                return [addr[:min_len] for addr in addresses]
    except Exception as e:
        parse_except(e)
    return None

def __get_tokenid_list(atype, mtype, chain = None):
    try:
        return [dict.get("tokenid") for dict in setting.address_list.get(atype) \
                if dict["type"] == mtype and mtype is not None and (chain is None or dict["chain"] == chain)]
    except Exception as e:
        parse_except(e)
    return None

def get_receiver_address_list(mtype, chain = None, full = True):
    try:
        return __get_address_list("receiver", mtype, chain)
    except Exception as e:
        parse_except(e)
    return None

def get_sender_address_list(mtype, chain = None, full = True):
    try:
        return __get_address_list("sender", mtype, chain)
    except Exception as e:
        parse_except(e)
    return None


def get_module_address(mtype, chain = None, full = True):
    try:
        ms = __get_address_list("module", mtype, chain)
        if ms is None or len(ms) == 0:
            return None
        assert len(ms) == 1, f"coin type({mtype}) chain({chain}) found multi module found, check it"
        return ms[0]
    except Exception as e:
        parse_except(e)
    return None

def get_token_address(mtype, chain = None, full = True):
    try:
        ms = __get_address_list("token", mtype, chain)
        if ms is None or len(ms) == 0:
            return None
        assert len(ms) == 1, f"token type({mtype}) chain({chain}) found multi coins found, check it"
        return ms[0]
    except Exception as e:
        parse_except(e)
    return None

def get_combine_address(mtype = "b2v", chain = "btc", full = True):
    try:
        ms = __get_address_list("combine", mtype, chain)
        if ms is None or len(ms) == 0:
            return none
        assert len(ms) == 1, f"({mtype}) chain({chain}) found multi combin address , check it"
        return ms[0]
    except Exception as e:
        parse_except(e)
    return None

def get_token_id(mtype = "b2v", chain = "btc"):
    try:
        ms = __get_tokenid_list("token", mtype, chain)
        if ms is None or len(ms) == 0:
            return None
        assert len(ms) == 1, f"({mtype}) chain({chain}) found multi token id({ms}), check it"
        return ms[0]
    except Exception as e:
        parse_except(e)
    return None


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

def get_conf():
    infos = {}
    mtypes = ["v2b", "v2l", "l2v", "b2v", "vfilter", "lfilter"]
    for mtype in mtypes:
        info = {}
        info["receiver"] = get_receiver_address_list(mtype)
        info["sender"] = get_sender_address_list(mtype)
        info["module"] = get_module_address(mtype, 'violas')
        info["db"] = get_db(mtype)
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


if __name__ == "__main__":
    main()
