#!/usr/bin/python3
import operator
import sys, getopt
from time import sleep
import json
import os
import time
import signal
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
        violaswallet, 
        violasserver
        )
from vlsopt.violasproof import (
        violasproof
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
from comm.values import(
        trantypebase as trantype,
        datatypebase as datatype
        )
from comm.amountconver import (
        amountconver
        )

from enum import Enum
from vrequest.request_client import requestclient
from analysis.analysis_filter import afilter
from dataproof import dataproof

name = "testmapping"
logger = log.logger.getLogger(name)
class Tokens(Enum):
    VIOLAS_BTC = "vBTC"
    VIOLAS_USDT = "vUSDT"
    BTC_BTC  = "BTC"
    ETHEREUM_USDT = "usdt"

def get_token_name(chain, token):
    return Tokens[f"{chain.upper()}_{token.upper()}"].value

'''
violas or libra client
'''

def init_stmanage():
    stmanage.set_conf_env("../bvexchange.toml")

def get_violasclient(chain = "violas"):
    init_stmanage()
    if chain == "libra":
        return violasproof(name, stmanage.get_libra_nodes(), chain)
    return violasproof(name, stmanage.get_violas_nodes(), chain)

def get_violaswallet(chain = "violas"):
    init_stmanage()
    return violaswallet(name, dataproof.wallets(chain), chain)

'''
ethereum client
'''
def get_ethclient(usd_erc20 = True, chain = "ethereum"):
    init_stmanage()
    client = ethclient(name, stmanage.get_eth_nodes(), chain)
    client.load_vlsmproof(stmanage.get_eth_token("vlsmproof")["address"])
    if usd_erc20:
        tokens = client.get_token_list().datas
        logger.debug(f"support tokens: {tokens}")
        for token in tokens:
            client.load_contract(token)
    return client
    
def get_ethwallet(chain = "ethereum"):
    init_stmanage()
    return ethwallet(name, dataproof.wallets("ethereum"), chain)

'''
btc client
'''

def get_btcclient():
    init_stmanage()
    return btcclient(name, stmanage.get_btc_conn())

def get_btcwallet():
    init_stmanage()
    return btcwallet(name, dataproof.wallets("btc"))

'''
proof client
'''
def get_proofclient(dtype = "e2vm"):
    init_stmanage()
    return requestclient(name, stmanage.get_db(dtype))

def is_violas_tran_mark(dtype, datas):
    tran_data = json.loads(datas) if isinstance(datas, str) else datas
    data = json.loads(tran_data.get("data", {}))

    return data.get("flag") == "violas" and data.get("type") == f"{dtype}_mark"

def get_tran_id(dtype, datas):
    tran_data = json.loads(datas) if isinstance(datas, str) else datas
    data = json.loads(tran_data.get("data"))
    return data.get("tran_id")

def test_e2vm():

    ewallet = get_ethwallet()
    eclient = get_ethclient()
    vclient = get_violasclient()
    max_work_time = 180

    #send usdt token, to mapping violas-USDT
    from_address    = stmanage.get_map_address("e2vm", "ethereum")

    #proof contract, recevie approve
    to_address      = eclient.get_proof_contract_address("main").datas

    #will received violas-usdt, and set it to proof's datas
    vls_receiver    = stmanage.get_receiver_address_list("v2em", "violas")[0] #DD user

    #from these address get transaction, checkout exchange-e2vm transaction, get payment amount(usdt)
    vls_e2vm_senders  = stmanage.get_sender_address_list("e2vm", "violas") 


    vclient._logger.debug(f'''
    vls receiver = {vls_receiver}
    from address = {from_address}
    to address = {to_address}
    vls_e2vm_senders  = {vls_e2vm_senders}
            ''')

    ret = eclient.get_token_list()
    assert ret.state == error.SUCCEED, "get tokens failed."
    token_ids = ret.datas

    
    ret = ewallet.get_account(from_address)
    assert ret.state == error.SUCCEED, f"get account(from_address) failed"
    account = ret.datas

    for token_id in token_ids:
        if not work_continue():
            break

        start_time = time.time()
        ret = eclient.get_token_min_amount(token_id)
        assert ret.state == error.SUCCEED, f"get {token_id} min amount failed"
        amount = max(2000, ret.datas)

        ret = eclient.get_address_sequence(from_address)
        assert ret.state == error.SUCCEED, ret.message
        sequence = ret.datas

        ret = eclient.allowance(from_address, to_address, token_id)
        assert ret.state == error.SUCCEED, ret.message

        #make approve to 0
        if ret.datas > 0:
            ret = eclient.approve(account, to_address, 0, token_id)
            assert ret.state == error.SUCCEED, ret.message

        ret = eclient.approve(account, to_address, amount, token_id)
        assert ret.state == error.SUCCEED, ret.message
        eclient._logger.debug(f"allowance amount :{eclient.allowance(from_address, to_address, token_id).datas}")

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
        while new_sequence <= sequence and work_continue():
            ret = eclient.get_address_sequence(from_address)
            assert ret.state == error.SUCCEED, ret.message
            new_sequence = ret.datas
            sleep(2)
            assert time.time() - start_time < max_work_time, f"time out, {from_address} sequence not changed"

        #get transaction info with from_address, sequence
        ret = eclient.get_transaction_version(from_address, new_sequence)
        assert ret.state == error.SUCCEED, ret.message
        version = ret.datas

        #wait state changed, get amount, usdt transfer maybe have transaction fee
        state = "start"
        map_amount = 0 
        while state == "start" and work_continue():
            ret = eclient.get_transactions(version, 1)
            assert ret.state == error.SUCCEED, ret.message
            tran = ret.datas[0]
            state = tran.get_state()
            map_amount = tran.get_amount()
            info = afilter.get_tran_data(tran, False)
            map_tran_id = get_tran_id("e2vm", info)
            
            sleep(2)
            assert time.time() - start_time < max_work_time, f"time out, eth proof {version} state not changed, check usdt transaction"

        #if state changed to end, check some value
        if state == "end":
            mapping_ok = False
            while not mapping_ok and work_continue():
                #check out mapping transaction
                for sender in vls_e2vm_senders:
                    if mapping_ok:
                        break
                    start_sequence = vls_e2vm_senders_sequence.get(sender) + 1
                    ret = vclient.get_address_sequence(sender)
                    assert ret.state == error.SUCCEED, f"get_address_sequence failed. {ret.message}"
                    latest_sequence = ret.datas
                    while (not mapping_ok) and start_sequence <= latest_sequence and work_continue():
                        ret = vclient.get_transaction_version(sender, start_sequence)
                        assert ret.state == error.SUCCEED, ret.message
                        new_version = ret.datas

                        ret = vclient.get_transactions(new_version, 1, True)
                        assert ret.state == error.SUCCEED, ret.message
                        tran = ret.datas[0] 
                        info = afilter.get_tran_data(tran, "violas")

                        start_sequence += 1
                        if not is_violas_tran_mark("e2vm", info):
                            vclient._logger.debug("not tran mark, check next...")
                            continue

                        tran_tran_id = get_tran_id("e2vm", info)
                        tran_receiver = info.get("receiver")
                        tran_sender  = info.get("sender")
                        tran_amount = info.get("amount")
                        tran_token_id = info.get("token_id")

                        if tran_tran_id == map_tran_id and vls_receiver == tran_receiver:
                            assert tran_amount == map_amount, "mapping amount is error. eth-{token_id} amount = {map_amount}, but violas-{tran_token_id} amount is {tran_amount}"
                            mapping_ok = True
                            print(f"mapping succeed. check violas address: version = {new_version}, receiver = {vls_receiver}, amount = {map_amount}")
                            return
                #else:
                #    assert False, f"not found transaction for mapping {token_id}, check tran_id = {map_tran_id} in {vls_e2vm_senders_sequence}"


def test_v2em():
    ewallet = get_ethwallet()
    eclient = get_ethclient()
    vclient = get_violasclient()
    vwallet = get_violaswallet()
    max_work_time = 180
    map_amount = 1_00_0000
    map_token_id = "USDT"
    eth_token_name = "usdt"

    #received eth-usdt address(mapping result)
    usdt_receiver = '0xf3FE0CB3b0c8Ab01631971923CEcDd14D857358A'
    
    #from this address send v2em request(violas transaction)
    from_address = stmanage.get_sender_address_list(datatype.E2VM, trantype.VIOLAS)[0]

    #receive v2em request, DD-account
    to_address = stmanage.get_receiver_address_list(datatype.V2EM, trantype.VIOLAS)[0]
    metadata = vclient.create_data_for_start(trantype.VIOLAS, datatype.V2EM, usdt_receiver)

    vclient._logger.debug(f'''
    usdt receiver = {usdt_receiver}
    send usdt address = {from_address}
    recever mapping receiver = to_address
    metadata = {metadata}
            ''')
    ret = vwallet.get_account(from_address)
    assert ret.state == error.SUCCEED, f"get {from_address} account failed. {ret.message}"
    map_sender = ret.datas

    before_usdt_amount = eclient.get_balance(usdt_receiver, eth_token_name).datas
    ret = vclient.send_coin(map_sender, to_address, map_amount, map_token_id, data = metadata)
    assert ret.state == error.SUCCEED, f"send coin faild from = {from_address} to_address = {to_address} metadata = {metadata}. {ret.message}"
    vclient._logger.debug(f"send coin result: {ret}")
    txn = ret.datas

    start_time = int(time.time())
    while start_time + max_work_time >= int(time.time()) and work_continue():
        after_usdt_amount = eclient.get_balance(usdt_receiver, eth_token_name).datas
        if after_usdt_amount > before_usdt_amount:
            vclient._logger.debug(f"mapping ok, mapping to {usdt_receiver} {eth_token_name} amount  {after_usdt_amount - before_usdt_amount}, input amount is {map_amount}")
            return

        message_wheel(max_work_time, start_time)

    if work_continue():
        assert False, f"time out, check bridge server is working...{txn}"

def test_b2vm():
    bwallet = get_btcwallet()
    bclient = get_btcclient()
    vclient = get_violasclient()
    vwallet = get_violaswallet()
    max_work_time = 180

    #violas-BTC : bitcoin-BTC = 1 : 100
    map_amount = 1_0_0000 #satoshi 1_0000_0000 = 1 BTC
    
    #send BTC from this address
    from_address = '2MyMHV6e4wA2ucV8fFKzXSEFCwrUGr2HEmY'
    assert bwallet.address_is_exists(from_address), f"sender {from_address} is not found in btc wallet"

    #association btc account, receive btc from other btc wallet, only send  btc to this account, can mapping vls-btc
    to_address = stmanage.get_receiver_address_list(datatype.B2VM, trantype.BTC)[0]
    assert bwallet.address_is_exists(to_address), f"association btc account {to_address} is not found in btc wallet"

    #send vls_btc_sender: get transaction(b2vm) from this account, check b2vm is succeed
    vls_btc_sender = stmanage.get_sender_address_list(datatype.B2VM, trantype.VIOLAS)
    found_vbs = vwallet.has_account_by_address(vls_btc_receiver).datas
    assert found_vbs == True, f"not found violas chain sender({vls_btc_sender}) of btc token"

    #receive violas-BTC from b2vm: payee   this account is not other payment
    vls_btc_receiver = stmanage.get_receiver_address_list(datatype.V2BM, trantype.VIOLAS)[0]
    found_vbr = vwallet.has_account_by_address(vls_btc_receiver).datas
    assert found_vbr == True, f"not found violas chain receiver({vls_btc_receiver}) of btc token"
    sequence = int(time.time())
    btc_module = "00000000000000000000000000000001"

    vclient._logger.debug(f'''
    vBTC receiver = {vls_btc_receiver}
    from address = {from_address}
    to address = {to_address}
    vls_btc_sender  = {vls_btc_sender}
            ''')
    #mark vls-btc-sender current sequence
    ret = vclient.get_address_sequence(vls_btc_sender)
    assert ret.state == error.SUCCEED, ret.message
    sender_start_sequence = ret.datas

    #mark currenct BTC amount
    ret = vclient.get_balance(vls_btc_receiver, "BTC", None)
    assert ret.state == ret.SUCCEED, f"get balance({vls_btc_receiver}, 'BTC') failed. {ret.message}"
    before_btc_amount = ret.datas

    btc_amount = amountconver(map_amount, amountconver.amounttype.BTC).amount(amountconver.amounttype.BTC)
    ret = bclient.sendexproofstart(datatype.B2VM.vaule, from_address, to_address, btc_amount, sequence, btc_module)
    assert ret.state == ret.SUCCEED, f"sendexproofstart failed. {ret.message}"
    txid = ret.datas
    map_tran_id = f"{from_address}_{sequence}"

    start_time = int(time.time())
    while start_time + max_work_time >= int(time.time()) and work_continue():
        ret = client.call_original_cli("getrawtransaction", txid, True)

        if ret.state != error.SUCCEED:
            message_wheel(max_work_time, start_time)
            continue

        tran_info = ret.datas
        confirmations = tran_info.get("confirmations")
        if confirmations <= 0:
            message_wheel(max_work_time, start_time)
            continue


    #will increase btc amount of vls_btc_receiver
    b2vm_amount = amountconver(map_amount, amountconver.amounttype.BTC).microamount(amountconver.amounttype.VIOLAS)
    #wait 30 s, make sure v2bm is exchange, may be check transaction is more acurrate ??????, here is use Ideal state
    start_time = int(time.time())
    while start_time + max_work_time >= int(time.time()) and work_continue():
        #mark vls-btc-sender current sequence
        ret = vclient.get_address_sequence(vls_btc_sender)
        assert ret.state == error.SUCCEED, ret.message
        sender_latest_sequence = ret.datas
        if sender_latest_sequence == sender_start_sequence:
            message_wheel(10, int(time.time()))
            continue

        while sender_start_sequence < sender_latest_sequence:
            sender_start_sequence += 1
            ret = vclient.get_transaction_version(vls_btc_sender, sender_start_sequence)
            assert ret.state == ret.SUCCEED, f"get_transaction_version({vls_btc_sender}, {sender_start_sequence}) failed. {ret.message}"
            new_version = ret.datas

            ret = vclient.get_transactions(new_version, 1, True)
            assert ret.state == ret.SUCCEED, f"get_transactions({new_version}) failed. {ret.message}"
            
            tran = ret.datas[0] 
            info = afilter.get_tran_data(tran, "violas")

            if not is_violas_tran_mark("b2vm", info):
                vclient._logger.debug("not tran mark, check next...")
                continue

            tran_tran_id = get_tran_id("b2vm", info)
            tran_receiver = info.get("receiver")
            tran_sender  = info.get("sender")
            tran_amount = info.get("amount")
            tran_token_id = info.get("token_id")

            if tran_tran_id == map_tran_id and vls_btc_receiver == tran_receiver:
                assert tran_amount == map_amount, "mapping amount is error. eth-{token_id} amount = {map_amount}, but violas-{tran_token_id} amount is {tran_amount}"
                mapping_ok = True
                print(f"mapping succeed. check violas address: version = {new_version}, receiver = {vls_receiver}, amount = {map_amount}")
                return

def test_v2bm():
    bwallet = get_btcwallet()
    bclient = get_btcclient()
    vclient = get_violasclient()
    vwallet = get_violaswallet()
    map_token_id = get_token_name("violas", "btc")
    max_work_time = 180

    #violas-BTC : bitcoin-BTC = 1 : 100
    map_amount = 1_000 # == 1_00_0000 satoshi

    from_address = stmanage.get_sender_address_list(datatype.B2VM, trantype.VIOLAS)[0]
    found_fa = vwallet.has_account_by_address(from_address).datas
    assert found_fa == True, f"not found violas chain sender({from_address}) of btc token"

    to_address = stmanage.get_receiver_address_list(datatype.V2BM, trantype.VIOLAS)[0]
    found_ta = vwallet.has_account_by_address(to_address).datas
    assert found_ta == True, f"not found violas chain sender({to_address}) of btc token"

    #receive BTC in bitcoin chain
    btc_receiver = '2MyMHV6e4wA2ucV8fFKzXSEFCwrUGr2HEmY'
    assert bwallet.address_is_exists(btc_receiver), f"sender {btc_receiver} is not found in btc wallet"

    before_btc_amount = bclient.get_balance(btc_receiver).datas
    metadata = vclient.create_data_for_start(trantype.VIOLAS, datatype.V2BM, btc_receiver)
    vclient._logger.debug(f'''
    btc receiver = {btc_receiver}
    send btc address = {from_address}
    recever mapping receiver = to_address
    metadata = {metadata}
            ''')

    ret = vwallet.get_account(from_address)
    assert ret.state == error.SUCCEED, f"get {from_address} account failed. {ret.message}"
    map_sender = ret.datas

    ret = vclient.send_coin(map_sender, to_address, map_amount, map_token_id, data = metadata)
    assert ret.state == error.SUCCEED, f"send coin faild from = {from_address} to_address = {to_address} metadata = {metadata}. {ret.message}"
    vclient._logger.debug(f"send coin result: {ret}")
    txn = ret.datas

    start_time = int(time.time())
    while start_time + max_work_time >= int(time.time()) and work_continue():
        after_btc_amount = bclient.get_balance(btc_receiver).datas
        if after_btc_amount > before_btc_amount:
            vclient._logger.debug(f"mapping ok, mapping to {btc_receiver} amount  {after_btc_amount - before_btc_amount}, input amount is {map_amount}")
            return

        message_wheel(max_work_time, start_time)

    if work_continue():
        assert False, f"time out, check bridge server is working...{txn}"

def message_wheel(max_work_time, start_time, sleep_secs = 2):   
        print(f"\r\bRemaining time = {max_work_time - int(time.time() - start_time)}(s) will sleeping... {sleep_secs} s", end = "") 
        sleep(sleep_secs)

_work_continue = True
def signal_stop(signal, frame):
    try:
        global _work_continue
        print("start signal : %i", signal )
        _work_continue = False
    except Exception as e:
        parse_except(e)
    finally:
        print("end signal")


def work_continue():
    return _work_continue

def init_signal():
    signal.signal(signal.SIGINT, signal_stop)
    signal.signal(signal.SIGTSTP, signal_stop)
    signal.signal(signal.SIGTERM, signal_stop)

if __name__ == "__main__":
    init_signal()
    ##test_e2vm()
    #test_v2em()
    #test_b2vm()
    test_v2bm()


