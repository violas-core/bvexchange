#!/usr/bin/python3
import operator
import sys, getopt
from time import sleep
import json
import os
sys.path.append(os.getcwd())
sys.path.append("..")
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
import log
import log.logger
import traceback
import datetime
import sqlalchemy
import stmanage
import requests
import comm
import comm.error
import comm.result
from comm.result import result
from comm.error import error
from comm.parseargs import parseargs
from comm.functions import json_print
from vlsopt.violasclient import (
        violasclient, 
        violaswallet, 
        violasserver
        )
from btc.btcclient import (
        btcclient
        )
from btc.btcwallet import (
        btcwallet
        )
from ethopt.ethclient import (
        ethclient,
        ethwallet
        )
from enum import Enum
from vrequest.request_client import requestclient
from analysis.analysis_filter import afilter
from dataproof import dataproof

'''
violas or libra client
'''
def get_violasclient(chain = "violas"):
    if chain == "libra":
        return violasclient(name, stmanage.get_libra_nodes(), chain)
    return violasclient(name, stmanage.get_violas_nodes(), chain)

def get_violaswallet(chain = "violas"):
    return violaswallet(name, dataproof.wallets(chain), chain)

'''
ethereum client
'''
def get_ethclient(usd_erc20 = True, chain = "ethereum"):
    client = ethclient(name, stmanage.get_eth_nodes(), chain)
    client.load_vlsmproof(stmanage.get_eth_token("vlsmproof")["address"])
    if usd_erc20:
        tokens = client.get_token_list().datas
        logger.debug(f"support tokens: {tokens}")
        for token in tokens:
            client.load_contract(token)
    return client
    
def get_ethwallet(, chain = "ethereum"):
    return ethwallet(name, dataproof.wallets("ethereum"), chain)

'''
btc client
'''

def getbtcclient():
    return btcclient(name, stmanage.get_btc_conn())

def getbtcwallet():
    return btcwallet(name, dataproof.wallets("btc"))

'''
proof client
'''
def get_proofclient(dtype = "e2vm"):
    return requestclient(name, stmanage.get_db(dtype))

def is_violas_tran(dtype, datas):
    tran_data = json.loads(datas) if isinstance(datas, str) else datas
    return tran_data.get("flag") == "violas" and tran_data.get("type") == f"{dtype}_mark"

def get_tran_id(dtype, datas):
    tran_data = json.loads(datas) if isinstance(datas, str) else datas
    data = json_loads(tran_data.get("data"))
    return data.get("tran_id")

def test_e2vm():

    ewallet = get_ethwallet()
    eclient = get_ethclient()
    vclient = get_violasclient()
    max_work_time = 180

    from_address    = stmanage.get_map_address("e2vm", "ethereum")
    to_address      = eclient.get_proof_contract_address("main")
    vls_receiver    = stmanage.get_receiver_address_list("v2em", "violas")[0] #DD user
    vls_e2vm_senders  = stmanage.get_sender_address_list("e2vm", "violas") 


    ret = client.get_token_list()
    assert ret.state == error.SUCCEED, "get tokens failed."
    token_ids = ret.datas

    
    ret = wallet.get_account(from_address)
    assert ret.state == error.SUCCEED, f"get account(from_address) failed"
    account = ret.datas

    for token_id in token_ids:
        start_time = time.time()
        ret = eclient.get_token_min_amount(token_id)
        assert ret.state == error.SUCCEED, f"get {token_id} min amount failed"
        amount = max(1000, ret.datas)

        ret = eclient.get_address_sequence(from_address)
        assert ret.state == error.SUCCEED, ret.message
        sequence = ret.datas

        ret = eclient.approve(account, to_address, amount, token_id)
        assert ret.state == error.SUCCEED, ret.message
        print(f"allowance amount :{eclient.allowance(from_address, to_address, token_id).datas}")

        #get vls_e2vm_sender sequence before mapping e2vm
        vls_e2vm_senders_sequence = {}
        for sender in vls_e2vm_senders:
            ret = vclient.get_address_sequence(sender)
            assert ret.state == error.SUCCEED, ret.message
            vls_e2vm_senders_sequence.update({sender : ret.datas})

        #send proof to ethereum chain
        ret = eclient.send_proof(account, token_id, vls_receiver)
        assert ret.state == error.SUCCEED, ret.message
     
        #check sequence of from_address, make sure send_proof is succeed
        new_sequence = sequence
        while new_sequence <= sequence:
            ret = eclient.get_address_sequence(from_address)
            assert ret.state == error.SUCCEED, ret.message
            new_sequence = ret.datas
            sleep(2)
            assert time.time() - start_time < max_work_time, f"time out, {from_address} sequence not changed"

        #get transaction info with from_address, sequence
        ret = eclient.get_transaction_version(from_address, new_sequence)
        assert ret.state == error.SUCCEED, ret.message
        version = ret.datas

        #wait state changed
        state = "start"
        map_amount = 0 
        while state == "start"
            ret = eclient.get_transactions(version, 1)
            assert ret.state == error.SUCCEED, ret.message
            tran = ret.datas[0]
            state = tran.get_state()
            map_amount = tran.get_amount()
            info = afilter.get_tran_data(tran, False)
            map_tran_id = get_tran_id(info)
            
            sleep(2)
            assert time.time() - start_time < max_work_time, f"time out, {version} state not changed, check usdt transaction"

        #if state changed to end, check some value
        if state == "end":
            mapping_ok = False
            while not mapping_ok:
                #check out mapping transaction
                for sender in vls_e2vm_senders:
                    if mapping_ok:
                        break
                    start_sequence = vls_e2vm_senders_sequence.get("sender") + 1
                    ret = vclient.get_address_sequence(sender)
                    assert ret.state == error.SUCCEED, ret.message
                    latest_sequence = ret.datas
                    while (not mapping_ok) and start_version <= latest_sequence:
                        ret = vclient.get_transaction_version(sender, )
                        assert ret.state == error.SUCCEED, ret.message
                        new_version = ret.datas

                        ret = vclient.get_transactions(new_version, 1, True)
                        assert ret.state == error.SUCCEED, ret.message
                        tran = ret.datas[0] 
                        info = afilter.get_tran_data(tran, "violas")
                        if not is_violas_tran_mark("e2vm", info):
                            continue

                        tran_tran_id = get_tran_id(info)
                        tran_receiver = info.get("receiver")
                        tran_sender  = info.get("sender")
                        tran_amount = info.get("amount")
                        tran_token_id = info.get("token_id")

                        if tran_tran_id == map_tran_id:
                            assert tran_amount == map_amount, "mapping amount is error. eth-{token_id} amount = {map_amount}, but violas-{tran_token_id} amount is {tran_amount}"
                            mapping_ok = True
                else:
                    assert False, f"not found transaction for mapping {token_id}, check tran_id = {map_tran_id} in {vls_e2vm_senders_sequence}"

