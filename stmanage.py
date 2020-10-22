#!/usr/bin/python3
from setting import setting
import comm.values
from comm import result
from comm.result import parse_except
from comm.functions import get_address_from_full_address 
from comm.functions import json_print
from comm.values import trantypebase

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

def get_syncing_state():
    return setting.syncing_mod

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

def get_address_info(atype):
    return setting.address_list.get(atype)

def get_sender_address_list(mtype, chain = None, full = True):
    return __get_address_list("sender", mtype, chain, full)

def get_combine_address_list(mtype, chain = None, full = True):
    return __get_address_list("combine", mtype, chain, full)

def get_type_code(dtype, default = ""):
    return setting.type_code.get(dtype, default)

def get_exchang_chains(mtype):
    _map_chain_name = {}
    for ttb in trantypebase:
        name = ttb.name.lower()
        _map_chain_name.update({name[:1]:name})
    return (_map_chain_name[mtype[:1]], _map_chain_name[mtype[2:3]])

def get_token_form_to_with_type(etype, mtype):
    f_t_coins = {}
    fchain, tchain = get_exchang_chains(mtype)
    if etype == "map":
        if fchain == "violas":
            fcoins = get_support_map_token_id(fchain) 
            tcoins = get_support_stable_token_id(tchain) 
        else:
            fcoins = get_support_stable_token_id(fchain) 
            tcoins = get_support_map_token_id(tchain) 

        for fcoin in fcoins:
            tcoin = get_token_map(fcoin)
            if tcoin in tcoins: #get_support_stable_token_id(tchain):
                f_t_coins.update({fcoin:tcoin})

        f_t_coins = [{"from_coin": fcoin, "to_coin": tcoin} for fcoin, tcoin in f_t_coins.items()]

    elif etype == "swap":
        fcoins = get_support_stable_token_id(fchain)
        tcoin = get_type_stable_token(mtype)
        f_t_coins = [{"from_coin": fcoin, "to_coin": tcoin} for fcoin in fcoins]

    else:
        raise Exception(f"etype({etype}) is invalid. make sure value(map swap)")

    return f_t_coins # from to


def get_support_address_info(etype = None):
    support_mods = get_support_mods(etype)
    assert support_mods is not None, f"support_mods is invalid"
    addr_infos = []
    receiver_infos = get_address_info("receiver")
    for info in receiver_infos:
        if info.get("type") in support_mods:
            f_t_coins = get_token_form_to_with_type(etype, info.get("type"))
            info.update({"code":get_type_code(info.get("type")), \
                    "from_to_token": f_t_coins})
            addr_infos.append(info)

    return addr_infos


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
    db_info = dict(setting.db_default)
    dbs = [db for db in setting.db_list if db.get("db") == mtype and mtype is not None]
    if dbs is not None and len(dbs) > 0:
        if db_info:
            db_info.update(dbs[0])
        else:
            db_info= dict(dbs[0])
    if db_info:
        db_info.update({"db":mtype})
    assert db_info, f"not found db({mtype})info."
    return db_info

def get_libra_nodes():
    return setting.libra_nodes

def get_violas_servers():
    return setting.violas_servers

def get_eth_nodes():
    return setting.ethereum_nodes

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
    if chain == "violas":
        #get map tokens only violas use
        for opthead in ["v2l", "v2b", "v2e"]:
            mtokens = [tokens.get("mtoken") for typename, tokens in setting.type_token.items() \
                if typename.startswith(opthead) and tokens.get("mtoken")]
            mtoken_list.extend(mtokens)
    
    return list(set(mtoken_list))

def get_support_stable_token_id(chain):
    assert chain is not None, "chain is violas/libra/btc/ethereum"
    stoken_list = []
    opthead = [] 
    if chain == "violas":
        #get map tokens only violas use
        optheads = ["l2v", "b2v"]
    elif chain == "libra":
        optheads = ["v2l"]
    elif chain == "btc":
        optheads = ["v2b"]
    elif chain == "ethereum":
        optheads = ["v2e"]

    #get target chain stable token
    for opthead in optheads:
        stoken_list += [tokens.get("stoken") for typename, tokens in setting.type_token.items() \
            if typename.startswith(opthead) and tokens.get("stoken")]
    
    return list(set(stoken_list))

def get_support_token_id(chain):
    assert chain is not None, "chain is violas/libra/btc/ethereum"
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
        run_state = opts.get("run", False)
        if run_state == True:
            mods.append(typename)
    return mods


def get_support_mods(etype = None):
    return setting.type_token_filter(etype)
    
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

def get_eth_token(name = None):
    tokens = []
    for key, token in setting.ethereum_tokens.items():
        if token.get("support", True):
            token["name"] = key
            tokens.append(token)

    if name:
        return setting.ethereum_tokens[name]
    return tokens

def main():
    set_conf_env("bvexchange.toml")
    mtypes = ["v2bm", "v2lm", "l2vm", "b2vm", "vfilter", "lfilter"]

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
    print(f"get token_map(USDT)->USDT: {get_token_map('USDT')}")
    print(f"get support_stable_token_id(libra)->Coin1 Coin2: {get_support_stable_token_id('libra')}")
    print(f"get support_stable_token_id(violas)->VLSUSD VLSEUR VLSSGD VLSGBP: {get_support_stable_token_id('violas')}")
    print(f"get support_map_token_id(libra)->[]: {get_support_map_token_id('libra')}")
    print(f"get support_map_token_id(violas)->BTC EUR USD USDT: {get_support_map_token_id('violas')}")
    print(f"get support_map_token_id(ethereum)->[]: {get_support_map_token_id('ethereum')}")
    print(f"get support_token_id(libra)->Coin1 Coin2: {get_support_token_id('libra')}")
    print(f"get support_token_id(violas)->VLSUSD VLSEUR VLSSGD VLSGBP BTC USD EUR: {get_support_token_id('violas')}")
    print(f"get support_token_id(btc)->BTC: {get_support_token_id('btc')}")
    print(f"get support_token_id(ethereum)->USDT: {get_support_token_id('ethereum')}")
    print(f"get swap module(violas): {get_swap_module()}")
    print(f"get swap owner(violas): {get_swap_owner()}")
    print(f"combin address(b2vusd, btc): {get_combine_address('b2vusd', 'btc')}")
    print(f"combin address(l2b, violas): {get_combine_address('l2b', 'violas')}")
    print(f"run mods: {get_run_mods()}")
    print(f"syncing state:{get_syncing_state()}")
    print("receiver info(map):")
    json_print(get_support_address_info("map"))
    print("receiver info(swap):")
    json_print(get_support_address_info("swap"))
    print("eth token info(None):")
    json_print(get_eth_token())
    print("eth token info(usdt):")
    json_print(get_eth_token("usdt"))

    #json_print(get_conf())

if __name__ == "__main__":
    main()
