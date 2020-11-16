#!/usr/bin/python3
import comm.values
from comm import result
from comm.result import parse_except
from comm.functions import get_address_from_full_address 
from comm.functions import json_print
from comm.values import trantypebase
from comm.values import map_chain_name
from dataproof.dataproof import setting

VIOLAS_ADDRESS_LEN = comm.values.VIOLAS_ADDRESS_LEN


class token_info():
    def __init__(self, token_info):
        self.__parse_token_info(token_info)

    def __parse_token_info(self, token_info):
        self.__chain_tokens = {}
        self.__mapping_tokens = {}
        self.__mapping_tokens_unique = {}
        self.__chain_names = set([])
        for chain, tokens in token_info["tokens"].items():
            token = tokens.get("token", [])
            mtoken = tokens.get("mtoken", [])
            self.__chain_tokens.update({chain: {"token": token, "mtoken": mtoken}})
            self.__chain_names.add(chain)

        for mtokens in token_info["mapping"]:
            chain_token = mtokens["token"].split(".")
            chain_mtoken = mtokens["mtoken"].split(".")

            key = f"{chain_token[0]}_{chain_mtoken[0]}"
            if key not in self.__mapping_tokens:
                self.__mapping_tokens.update({key: {}})
            self.__mapping_tokens[key].update({chain_token[1]:chain_mtoken[1]})

            key = f"{chain_mtoken[0]}_{chain_token[0]}"
            if key not in self.__mapping_tokens:
                self.__mapping_tokens.update({key: {}})
            self.__mapping_tokens[key].update({chain_mtoken[1]:chain_token[1]})

            #temp for, next version should fix 
            self.__mapping_tokens_unique.update({chain_mtoken[1]:chain_token[1]})
            self.__mapping_tokens_unique.update({chain_token[1]:chain_mtoken[1]})

    def check_chain_name(self, chain):
        assert chain in self.__chain_names, "chain is violas/libra/btc/ethereum"

    def get_tokens(self, chain):
        self.check_chain_name(chain)
        return self.__chain_tokens[chain].get("token", [])

    def get_mtokens(self, chain):
        self.check_chain_name(chain)
        return self.__chain_tokens[chain].get("mtoken", [])
    
    def get_can_mapping_all(self):
        return self.__mapping_tokens

    def get_can_mapping(self, from_chain, to_chain):
        self.check_chain_name(from_chain)
        self.check_chain_name(to_chain)
        return self.__mapping_tokens.get(f"{from_chain}_{to_chain}", [])

    def get_token_mapping_unique(self, token):
            return self.__mapping_tokens_unique.get(token)

    def get_token_mapping(self, token, from_chain, to_chain):
        self.check_chain_name(from_chain)
        self.check_chain_name(to_chain)
        return self.__mapping_tokens[f"{from_chain}_{to_chain}"].get(token)

token_manage = None #token_info(setting.token_info)
def check_setting():
    pass

def keys():
    return setting.setting.keys()

def get(key):
    return setting.setting.get(key)

def set_conf_env_default():
    setting.setting.set_conf_env_default()
    reset()

def set_conf_env(conffile):
    setting.setting.set_conf_env(conffile)
    reset()

def reset():
    setting.setting.reset()
    global token_manage
    token_manage = token_info(setting.setting.token_info)
    check_setting()

def get_conf_env():
    return setting.setting.get_conf_env()

def get_looping_sleep(mtype):
    sleep = int(setting.setting.looping_sleep.get(mtype, 1))
    return sleep

def get_syncing_state():
    return setting.setting.syncing_mod

def __get_address_list(atype, mtype, chain = None, full = True):
    ''' 
       full: get address type 
           True: auth_prefix + address 
           False: address
    '''
    addresses =  [dict.get("address") for dict in setting.setting.address_list.get(atype) \
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
#        return [dict.get("tokenid") for dict in setting.setting.address_list.get(atype) \
#                if dict["type"] == mtype and mtype is not None and (chain is None or dict["chain"] == chain)]
#    except Exception as e:
#        parse_except(e)
#    return None
#

def get_receiver_address_list(mtype, chain = None, full = True):
    return __get_address_list("receiver", mtype, chain, full)

def get_map_address(mtype, chain = None, full = True):
    return __get_address_list("map", mtype, chain, full)[0]

def get_address_info(atype):
    return setting.setting.address_list.get(atype)

def get_sender_address_list(mtype, chain = None, full = True):
    return __get_address_list("sender", mtype, chain, full)

def get_combine_address_list(mtype, chain = None, full = True):
    return __get_address_list("combine", mtype, chain, full)

def get_type_code(dtype, default = ""):
    return setting.setting.type_code.get(dtype, default)

def get_exchang_chains(mtype):
    from_chain  = map_chain_name[mtype[0]]
    to_chain    = map_chain_name[mtype[2]]
    return (from_chain, to_chain)

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
            tcoin = get_token_map(fcoin, mtype)
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

def type_is_map(mtype):
    opts = setting.setting.type_token.get(mtype)
    if opts:
        return opts.get("etype", "swap") == "map"
    return False

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
    db_info = dict(setting.setting.db_default)
    dbs = [db for db in setting.setting.db_list if db.get("db") == mtype and mtype is not None]
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
    return setting.setting.libra_nodes

def get_violas_servers():
    return setting.setting.violas_servers

def get_eth_nodes():
    return setting.setting.ethereum_nodes

def get_violas_nodes():
    return setting.setting.violas_nodes

def get_btc_nodes():
    return setting.setting.btc_conn

def get_btc_conn():
    return setting.setting.btc_conn

def get_traceback_limit():
    return setting.setting.traceback_limit

def get_db_echo():
    return setting.setting.db_echo

def get_max_times(mtype):
    return setting.setting.v2b_maxtimes

#get btc/libra chain stable's map token
def get_token_map(token, mtype = None):
    if mtype:
        (from_chain, to_chain) = get_exchang_chains(mtype)
        return token_manage.get_token_mapping(token, from_chain, to_chain)
    else:
        return token_manage.get_token_mapping_unique(token)


#get opttype' stable token(map, ...)
def get_type_stable_token(mtype = None):
    type_stable_token = {}
    for typename, tokens in setting.setting.type_token.items():
        if mtype is None or typename == mtype:
            if tokens.get("ttoken") is not None:
                type_stable_token.update({typename : tokens.get("ttoken")})

    if mtype:
        return type_stable_token.get(mtype)
    return type_stable_token

def get_support_map_token_id(chain, mtype = None):
    mtoken_list = []
    if chain and not mtype:
        mtoken_list = token_manage.get_mtokens(chain)
    elif mtype:
        (from_chain, to_chain) = get_exchang_chains(mtype)
        mtoken_list = token_manage.get_can_mapping(from_chain, to_chain)
    else:
        raise Exception("arguments(chain({chain}), mtype({mtype})) is invalid.")
    
    return list(set(mtoken_list))

def get_support_stable_token_id(chain):
    token_list = token_manage.get_tokens(chain)
    return list(set(token_list))

def get_support_token_id(chain):
    mtokens = token_manage.get_mtokens(chain)
    tokens = token_manage.get_tokens(chain)
    return list(set(mtokens + tokens))

def get_swap_module():
    return setting.setting.swap_module.get("address")

def get_swap_owner():
    return setting.setting.swap_owner.get("address")

def get_run_mods():
    mods = []
    for typename, opts in setting.setting.type_token.items():
        run_state = opts.get("run", False)
        if run_state == True:
            mods.append(typename)
    return mods


def get_support_mods(etype = None):
    return setting.setting.type_token_filter(etype)
    
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
    for key, token in setting.setting.ethereum_tokens.items():
        if token.get("support", True):
            token["name"] = key
            tokens.append(token)

    if name:
        return setting.setting.ethereum_tokens[name]
    return tokens

def get_vlsmproof_address():
    return get_eth_token("vlsmproof")["address"]

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
    print(f"get token_map(USDT)->usdt: {get_token_map('USDT')}")
    print(f"get token_map(usdt)->USDT: {get_token_map('usdt')}")
    print(f"get support_stable_token_id(libra)->Coin1 Coin2: {get_support_stable_token_id('libra')}")
    print(f"get support_stable_token_id(violas)->VLSUSD VLSEUR VLSSGD VLSGBP: {get_support_stable_token_id('violas')}")
    print(f"get support_map_token_id(libra)->[]: {get_support_map_token_id('libra')}")
    print(f"get support_map_token_id(violas)->BTC EUR USDT: {get_support_map_token_id('violas')}")
    print(f"get support_map_token_id(violas, v2em)->USDT: {get_support_map_token_id('violas', 'v2em')}")
    print(f"get support_map_token_id(violas, v2lm)->USD : {get_support_map_token_id('violas', 'v2lm')}")
    print(f"get support_map_token_id(violas, v2bm)->BTC: {get_support_map_token_id('violas', 'v2bm')}")
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
    print(f"support mods: {get_support_mods().keys()}")
    print(f"syncing state:{get_syncing_state()}")
    print("receiver info(map):")
    json_print(get_support_address_info("map"))
    print("receiver info(swap):")
    json_print(get_support_address_info("swap"))
    print("eth vlsmproof address(): 0xd1E73b216D9baC1dB6b4A790595304Ab6337a4D0")
    json_print(get_vlsmproof_address())

    #json_print(get_conf())

if __name__ == "__main__":
    main()
