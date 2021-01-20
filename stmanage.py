#!/usr/bin/python3
import comm.values
from comm import result
from comm.result import parse_except
from comm.functions import get_address_from_full_address 
from comm.functions import json_print
from comm.values import trantypebase
from comm.values import (
        map_chain_name, 
        workmod as work_mod, 
        datatypebase as datatype,
        trantypebase as trantype,
        dbindexbase as dbindex,
        langtype,
        )
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
        assert chain in self.__chain_names, f"{chain} is not in {self.__chain_names}"

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

    def get_violas_mtoken(self, token, chain):
        self.check_chain_name(chain)
        if chain == trantype.VIOLAS.value:
            return token
        return self.__mapping_tokens[f"{chain}_{trantype.VIOLAS.value}"].get(token)

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
    mtype = to_str_value(mtype)
    sleep = int(setting.setting.looping_sleep.get(mtype, 8))
    return sleep

def get_syncing_state():
    return setting.setting.syncing_mod

''' 
   full: get address type 
       True: auth_prefix + address 
       False: address
'''
def __get_address_list(atype, mtype, chain_name, full = True):
    chain = to_str_value(chain_name)
    mtype = to_str_value(mtype)
    #default addresses: only chain and type is not None
    default_addresses = [dict.get("address") for dict in setting.setting.address_list.get(atype) \
            if dict["type"] == "default" and mtype is not None and (chain is not None and dict.get("chain") == chain)]

    addresses =  [dict.get("address") for dict in setting.setting.address_list.get(atype) \
            if dict["type"] == mtype and mtype is not None and (chain is None or dict["chain"] == chain)]
    
    if addresses is None or len(addresses) < 1:
        addresses.extend(default_addresses)

    if addresses is not None and len(addresses) > 0:
        if full:
            return addresses
        else:
            min_len = min(VIOLAS_ADDRESS_LEN)
            assert min_len > 0 , "address min(VIOLAS_ADDRESS_LEN) is invalid."
            return [get_address_from_full_address(addr) for addr in addresses]
    return []


#maybe use. so keep it until libra support usd eur ...
#def __get_tokenid_list(atype, mtype, chain = None):
#    try:
#        return [dict.get("tokenid") for dict in setting.setting.address_list.get(atype) \
#                if dict["type"] == mtype and mtype is not None and (chain is None or dict["chain"] == chain)]
#    except Exception as e:
#        parse_except(e)
#    return None
#

def get_receiver_address_list(mtype, chain, full = True):
    return __get_address_list("receiver", mtype, chain, full)

def get_map_address(mtype, chain = None, full = True):
    return __get_address_list("map", mtype, chain, full)[0]

def get_request_funds_address_list(mtype = None, full = True):
    return __get_address_list("funds", mtype, trantype.VIOLAS, full)

def get_funds_address(full = True):
    return __get_address_list("receiver", "funds", trantype.VIOLAS.value, full)[0]

def get_receiver_msg_list(mtype, chain, full = True):
    return __get_address_list("receiver", "funds", trantype.VIOLAS.value, full)

def get_request_msg_address_list(mtype = None, full = True):
    return __get_address_list("msg", mtype, trantype.VIOLAS, full)
'''
   get address for violas account, which have permission for request funds
'''
def get_permission_request_funds_address(full = False):
    addrs = []

    #filter the address where you can apply for a token from bridge server
    valid_mods = get_support_mods()
    exchange_mods = [mod.value for mod in datatype]
    set(exchange_mods).intersection_update(set(valid_mods))
    for mod in valid_mods:
        # this mod is mtype(datatype)
        (from_chain, to_chain) = get_exchang_chains(mod)
        filter_addrs = []
        if from_chain and trantype(from_chain) == trantype.VIOLAS:
            filter_addrs = get_receiver_address_list(mod, trantype.VIOLAS.value, False)
        elif to_chain and trantype(to_chain) == trantype.VIOLAS:
            filter_addrs = get_sender_address_list(mod, trantype.VIOLAS.value, False)
        addrs.extend(filter_addrs)

    #Specify the address where you can apply for a token
    external_request = get_request_funds_address_list("map", False)
    addrs.extend(external_request)
    external_request = get_request_funds_address_list("liq", False)
    addrs.extend(external_request)
    return set(addrs)

def get_address_info(atype):
    mtypes = get_support_dtypes()
    address_info = []
    for mtype in mtypes:
        from_chain, to_chain = get_exchang_chains(mtype)
        if from_chain and to_chain:
            addresses = __get_address_list(atype, mtype, from_chain)
            infos = [{"address":address, "type":mtype, "chain":from_chain} for address in addresses]
            address_info.extend(infos)
    return address_info

def get_sender_address_list(mtype, chain, full = True):
    return __get_address_list("sender", mtype, chain, full)

def get_combine_address_list(mtype, chain, full = True):
    return __get_address_list("combine", mtype, chain, full)

def get_type_code(mtype, default = ""):
    mtype = to_str_value(mtype)
    return setting.setting.type_code.get(mtype, default)

def get_exchang_chains(mtype):
    mtype = to_str_value(mtype)
    from_chain = None
    to_chain = None
    try:
        from_chain  = map_chain_name.get(mtype[0])
        to_chain    = map_chain_name.get(mtype[2])
        token_id = get_token_id_from_fundstype(mtype)
        to_chain = get_trantype_with_token_id(token_id).value if token_id else to_chain
        from_chain =trantype.VIOLAS.value if type_is_funds(mtype) else from_chain
        from_chain = trantype.VIOLAS.value if type_is_msg(mtype) else from_chain
        to_chain = trantype.VIOLAS.value if type_is_msg(mtype) else to_chain
        
    except Exception as e:
        from_chain = None
        to_chain = None
    return (from_chain, to_chain)

def get_token_form_to_with_type(etype, mtype):
    mtype = to_str_value(mtype)
    f_t_coins = {}
    fchain, tchain = get_exchang_chains(mtype)
    if fchain is None and tchain is None:
        return f_t_coins

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
    mtype = to_str_value(mtype)
    opts = setting.setting.type_token.get(mtype)
    if opts:
        return opts.get("etype", "swap") == "map"
    return False

def type_is_funds(mtype):
    mtype = to_str_value(mtype)
    return mtype.startswith("funds")

def type_is_msg(mtype):
    mtype = to_str_value(mtype)
    return mtype.startswith("msg")
'''
get type_opts.etype = map/swap info(token map relation, address mtype code(btc) etc..)
@param etype map/swap/funds
'''
def get_support_address_info(etype = None):
    support_mods = get_support_mods_info(etype)
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

def get_trantype_with_token_id(token_id):
    for ttype in trantype:
        if ttype == trantype.UNKOWN:
            continue

        if token_id and token_id in [token.lower() for token in get_support_token_id(ttype)]:
            return ttype
    raise ValueError(f"not found support token id({token_id}) in {trantype}")

def get_target_nodes(ttype):
    target_ttype = ttype
    if isinstance(ttype, trantype):
        target_ttype = ttype.value
    
    assert isinstance(target_ttype, str), f"input args {ttype} can't convert str type"

    return globals()[f"get_{target_ttype}_nodes"]()

def get_libra_nodes():
    return setting.setting.libra_nodes

def get_violas_servers():
    return setting.setting.violas_servers

#get_target_nodes use this func
def get_ethereum_nodes():
    return get_eth_nodes()

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

def get_max_times():
    return setting("retry_maxtimes")

#get btc/libra chain stable's map token
def get_token_map(token, mtype = None):
    if mtype:
        (from_chain, to_chain) = get_exchang_chains(mtype)
        return token_manage.get_token_mapping(token, from_chain, to_chain)
    else:
        return token_manage.get_token_mapping_unique(token)

def to_str_value(data):
    if not data:
        return data
    return data.value if not isinstance(data, str) else data

def get_violas_mtoken(token, chain_name):
    chain = to_str_value(chain_name)
    return token_manage.get_violas_mtoken(token, chain_name)

#get opttype' stable token(map, ...)
def get_type_stable_token(mtype = None):
    mtype = to_str_value(mtype)
    type_stable_token = {}
    for typename, tokens in setting.setting.type_token.items():
        if mtype is None or typename == mtype:
            if tokens.get("ttoken") is not None:
                type_stable_token.update({typename : tokens.get("ttoken")})

    if mtype:
        return type_stable_token.get(mtype)
    return type_stable_token

def get_support_map_token_id(chain_name, mtype = None):
    chain = to_str_value(chain_name)
    mtype = to_str_value(mtype)
    mtoken_list = []
    if chain and not mtype:
        mtoken_list = token_manage.get_mtokens(chain)
    elif mtype:
        (from_chain, to_chain) = get_exchang_chains(mtype)
        mtoken_list = token_manage.get_can_mapping(from_chain, to_chain)
    else:
        raise Exception("arguments(chain({chain}), mtype({mtype})) is invalid.")
    
    return list(set(mtoken_list))

def get_support_stable_token_id(chain_name):
    chain = to_str_value(chain_name)
    token_list = token_manage.get_tokens(chain)
    return list(set(token_list))

def get_support_token_id(chain_name):
    chain = to_str_value(chain_name)
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
        run_state = opts.get("run")
        if run_state == True:
            mods.append(typename)
    return mods


def get_support_mods_info(etype = None):
    return setting.setting.type_token_filter(etype)
    
def get_support_mods():
    mods = []
    for typename, opts in setting.setting.type_token.items():
        mods.append(typename)
    return mods

def get_support_dtypes():
    mods = get_support_mods()
    return [mtype.value for mtype in datatype if mtype.value in mods]

def get_token_id_from_fundstype(funds_type):
    return funds_type[5:] if type_is_funds(funds_type) else None

def get_conf():
    infos = {}
    mtypes = get_support_dtypes()
    for mtype in mtypes:
        info = {}
        (from_chain, to_chain) = get_exchang_chains(mtype)
        addr_type = "funds" if type_is_funds(mtype) else mtype
    
        info["receiver"] = get_receiver_address_list(addr_type, from_chain)
        info["sender"] = get_sender_address_list(addr_type, to_chain)
        info["db"] = get_db(mtype)
        if info["db"] is not None:
            info["db"]["password"] = "password is keep secret"
            info["db"]["index"] = dbindex[mtype.upper()].value
        info["loop sleep"] = get_looping_sleep(mtype)
        info["combine"] = get_combine_address(mtype, from_chain)
        infos[mtype] = info
    infos["traceback limit"] = get_traceback_limit()
    infos["btc conn"] = get_btc_conn()
    infos["violas nodes"] = get_violas_nodes()
    infos["violas server"] = get_violas_servers()
    infos["libra nodes"] = get_libra_nodes()
    infos["max times"] = get_max_times()
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

def get_sms_nodes():
    return setting.setting.sms_conn
    
def get_sms_templetes():
    return list(setting.setting.sms_templete)

def get_sms_templete(lang = "ch"):
    if isinstance(lang, langtype):
        lang = lang.value

    for item in setting.setting.sms_templete:
        if item.get("lang", "") == lang:
            return item.get("data")
    raise ValueError("not found {lang} templete. check args and {setting.setting.sms_templete}")

def get_addressbook(dtype):
    return setting.setting.address_book

    
def get_support_msg_min_version(chain_name):
    chain = to_str_value(chain_name)
    return setting("msg_min_version").get(chain_name, 0)

'''
   get address for violas account, which have permission for request funds
'''
def get_permission_request_msg_address(full = False):
    addrs = []

    #filter the address where you can apply for a token from bridge server
    valid_mods = get_support_mods()
    exchange_mods = [mod.value for mod in datatype]
    set(exchange_mods).intersection_update(set(valid_mods))
    for mod in valid_mods:
        # this mod is mtype(datatype)
        (from_chain, to_chain) = get_exchang_chains(mod)
        filter_addrs = []
        if from_chain and trantype(from_chain) == trantype.VIOLAS:
            filter_addrs = get_receiver_address_list(mod, trantype.VIOLAS.value, full)
        elif to_chain and trantype(to_chain) == trantype.VIOLAS:
            filter_addrs = get_sender_address_list(mod, trantype.VIOLAS.value, full)
        addrs.extend(filter_addrs)

    #Specify the address where you can apply for a token
    external_request = get_request_msg_address_list("msg", full)
    addrs.extend(external_request)
    return set(addrs)

def main():
    set_conf_env("bvexchange.toml")
    mtypes = ["v2bm", "v2lm", "l2vm", "b2vm", "vfilter", "lfilter"]

    for mtype in mtypes:
        print(f"receiver address({mtype}): {get_receiver_address_list(mtype, trantype.VIOLAS)}")
        print(f"sender address({mtype}): {get_sender_address_list(mtype, 'violas')}")
        print(f"get db({mtype}): {get_db(mtype)}")
        print(f"get looping sleep({mtype}):{get_looping_sleep(mtype)}")
        print(f"combin address({mtype}): {get_combine_address(mtype, 'violas')}")

    print(f"get traceback limit: {get_traceback_limit()}")
    print(f"get btc_node: {get_btc_conn()}")
    print(f"get sms_nodes: {get_sms_nodes()}")
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
    print(f"get violas map token(usdt)->USDT: {get_violas_mtoken('usdt', 'ethereum')}")
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
    print(f"support mods info keys: {get_support_mods_info().keys()}")
    print(f"support mods == mods info keys: {get_support_mods()}")
    print(f"syncing state:{get_syncing_state()}")
    print("receiver info(map):")
    json_print(get_support_address_info("map"))
    print("receiver info(swap):")
    json_print(get_support_address_info("swap"))
    print("eth vlsmproof address(): 0xd1E73b216D9baC1dB6b4A790595304Ab6337a4D0")
    json_print(get_vlsmproof_address())
    print(f"max times = {get_max_times()}")
    print(f"hav permission request funds addresses = {get_permission_request_funds_address()}")
    print(f"get_support_dtypes:{get_support_dtypes()}")
    print(f"get sms templete(ch): {get_sms_templete('ch')}")
    print(f"get sms templete(en): {get_sms_templete('en')}")
    print(f"hav permission request msg addresses = {get_permission_request_msg_address()}")
    print(f"get msg min version : {get_support_msg_min_version('violas')}")



if __name__ == "__main__":
    main()
