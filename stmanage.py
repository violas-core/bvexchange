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
    setting.reset()

def set_conf_env(conffile):
    setting.set_conf_env(conffile)
    setting.reset()

def reset():
    setting.reset()

def get_conf_env():
    return setting.get_conf_env()

def get_looping_sleep(mtype):
    sleep = int(setting.looping_sleep.get(mtype, 1))
    return sleep

def __get_address_list(atype, mtype, chain = None, full = True):
    ''' 
       full: get address type 
           True: auth_prefix + address 
           False: address
    '''
    addresses =  [dict.get("address") for dict in setting.address_list.get(atype) \
            if dict["type"] == mtype and mtype is not None and (chain is None or dict["chain"] == chain)]
    if addresses is not None and len(addresses) > 0:
        if full:
            return addresses
        else:
            min_len = min(VIOLAS_ADDRESS_LEN)
            assert min_len > 0 , "address min(VIOLAS_ADDRESS_LEN) is invalid."
            return [get_address_from_full_address(addr) for addr in addresses]

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
    return __get_address_list("receiver", mtype, chain, full)

def get_sender_address_list(mtype, chain = None, full = True):
    return __get_address_list("sender", mtype, chain, full)

def get_combine_address_list(mtype, chain = None, full = True):
    return __get_address_list("combine", mtype, chain, full)

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

def get_combine_address(mtype, chain , full = True):
     ms = __get_address_list("combine", mtype, chain, full)
     if ms is None or len(ms) == 0:
         return None
     assert len(ms) == 1, f"({mtype}) chain({chain}) found multi combin address , check it"
     return ms[0]

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
    dbs = [dict for dict in setting.db_list if dict.get("db") == mtype and mtype is not None]
    if dbs is not None and len(dbs) > 0:
        return dbs[0]

def get_libra_nodes():
    return setting.libra_nodes

def get_violas_servers():
    return setting.violas_servers

def get_violas_nodes():
    return setting.violas_nodes

def get_btc_nodes():
    return setting.btc_conn

def get_btc_conn():
    return setting.btc_conn

def get_traceback_limit():
    return setting.traceback_limit

def get_db_echo():
    return setting.db_echo

def get_max_times(mtype):
    return setting.v2b_maxtimes

#get btc/libra chain stable's map token
def get_token_map(token = None):
    token_map = {}
    for typename, tokens in setting.type_token.items():
        if typename.startswith("v2") and tokens.get("stoken") and tokens.get("mtoken"): #v2b v2l
            token_map.update({tokens.get("stoken") : tokens.get("mtoken")})
            token_map.update({tokens.get("mtoken") : tokens.get("stoken")})
    if token:
        return token_map.get(token)
    return token_map

#get opttype' stable token
def get_type_stable_token(mtype = None):
    type_stable_token = {}
    for typename, tokens in setting.type_token.items():
        if mtype is None or typename == mtype:
            if tokens.get("stoken") is not None: 
                type_stable_token.update({typename : tokens.get("stoken")})

    if mtype:
        return type_stable_token.get(mtype)
    return type_stable_token

def get_type_map_token(mtype = None):
    type_map_token = {}
    for typename, tokens in setting.type_token.items():
        if mtype is None or typename == mtype:
            type_map_token.update({mtype : tokens.get("mtoken")})

    if mtype:
        return type_map_token.get(mtype)
    return type_map_token

def get_support_map_token_id(chain):
    assert chain is not None, "chain is violas/libra/btc"
    mtoken_list = []
    opthead = [] 
    if chain == "violas":
        #get map tokens only violas use
        for opthead in ["v2l", "v2b"]:
            mtokens = [tokens.get("mtoken") for typename, tokens in setting.type_token.items() \
                if typename.startswith(opthead) and tokens.get("mtoken")]
            mtoken_list.extend(mtokens)
    
    return list(set(mtoken_list))

def get_support_stable_token_id(chain):
    assert chain is not None, "chain is violas/libra/btc"
    stoken_list = []
    opthead = [] 
    if chain == "violas":
        #get map tokens only violas use
        optheads = ["l2v", "b2v"]
    elif chain == "libra":
        optheads = ["v2l"]
    elif chain == "btc":
        optheads = ["v2b"]

    #get target chain stable token
    for opthead in optheads:
        stoken_list += [tokens.get("stoken") for typename, tokens in setting.type_token.items() \
            if typename.startswith(opthead) and tokens.get("stoken")]
    
    return list(set(stoken_list))

def get_support_token_id(chain):
    assert chain is not None, "chain is violas/libra/btc"
    mtokens = get_support_map_token_id(chain)
    stokens = get_support_stable_token_id(chain)
    return list(set(mtokens + stokens))

def get_swap_module():
    return setting.swap_module.get("address")

def get_swap_owner():
    return setting.swap_owner.get("address")

def get_run_mods():
    mods = []
    for typename, opts in setting.type_token.items():
        run_state = opts.get("run", "false")
        if run_state.lower() == "true":
            mods.append(typename)
    return mods


def get_support_mods():
    return setting.type_token.keys()

    
def get_conf():
    infos = {}
    mtypes = ["v2b", "v2l", "l2v", "b2v", "vfilter", "lfilter"]
    for mtype in mtypes:
        info = {}
        info["receiver"] = get_receiver_address_list(mtype)
        info["sender"] = get_sender_address_list(mtype)
        info["db"] = get_db(mtype)
        if info["db"] is not None:
            info["db"]["password"] = "password is keep secret"
        info["loop sleep"] = get_looping_sleep(mtype)
        info["max times"] = get_max_times(mtype)
        info["combine"] = get_combine_address(mtype, "violas")
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
        print(f"get db({mtype}): {get_db(mtype)}")
        print(f"get looping sleep({mtype}):{get_looping_sleep(mtype)}")
        print(f"get max times({mtype})):{get_max_times(mtype)}")
        print(f"combin address({mtype}): {get_combine_address(mtype, 'violas')}")

    print(f"get traceback limit: {get_traceback_limit()}")
    print(f"get btc_node: {get_btc_conn()}")
    print(f"get violas nodes: {get_violas_nodes()}")
    print(f"get violas_servers: {get_violas_servers()}")
    print(f"get libra nodes: {get_libra_nodes()}")
    print(f"get db echo :{get_db_echo()}")
    print(f"get token_map: ")
    json_print(get_token_map())
    print(f"get type_stable_token: ")
    json_print(get_type_stable_token())
    print(f"get type_stable_token(l2vusd)->VLSUSD: {get_type_stable_token('l2vusd')}")
    print(f"get type_stable_token(l2vgbp)->VLSGBP: {get_type_stable_token('l2vgbp')}")
    print(f"get type_stable_token(v2lusd)-Coin1: {get_type_stable_token('v2lusd')}")
    print(f"get type_stable_token(l2b)->BTC: {get_type_stable_token('l2b')}")
    print(f"get type_stable_token(b2lusd)->Coin1: {get_type_stable_token('b2lusd')}")
    print(f"get type_stable_token(b2leur)->Coin2: {get_type_stable_token('b2leur')}")
    print(f"get type_stable_token(l2b)->btc: {get_type_stable_token('l2b')}")
    print(f"get type_stable_token(b2lusd)->Coin1: {get_type_stable_token('b2lusd')}")
    print(f"get token_map(Coin1)->USD: {get_token_map('Coin1')}")
    print(f"get token_map(Coin2)->EUR: {get_token_map('Coin2')}")
    print(f"get token_map(BTC)->BTC: {get_token_map('BTC')}")
    print(f"get token_map(USD)->Coin1: {get_token_map('USD')}")
    print(f"get token_map(EUR)->Coin2: {get_token_map('EUR')}")
    print(f"get support_stable_token_id(libra)->Coin1 Coin2: {get_support_stable_token_id('libra')}")
    print(f"get support_stable_token_id(violas)->VLSUSD VLSEUR VLSSGD VLSGBP: {get_support_stable_token_id('violas')}")
    print(f"get support_map_token_id(libra)->[]: {get_support_map_token_id('libra')}")
    print(f"get support_map_token_id(violas)->BTC EUR USD: {get_support_map_token_id('violas')}")
    print(f"get support_token_id(libra)->Coin1 Coin2: {get_support_token_id('libra')}")
    print(f"get support_token_id(violas)->VLSUSD VLSEUR VLSSGD VLSGBP BTC USD EUR: {get_support_token_id('violas')}")
    print(f"get support_token_id(btc)->BTC: {get_support_token_id('btc')}")
    print(f"get swap module(violas): {get_swap_module()}")
    print(f"get swap owner(violas): {get_swap_owner()}")
    print(f"combin address(b2vusd, btc): {get_combine_address('b2vusd', 'btc')}")
    print(f"combin address(l2b, violas): {get_combine_address('l2b', 'violas')}")
    print(f"run mods: {get_run_mods()}")

    #json_print(get_conf())

if __name__ == "__main__":
    main()
