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
from comm.functions import (
    json_print,
    split_full_address,
    output_args_func
        )
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
    VIOLAS_BTC      = "VBTC"
    VIOLAS_USDT     = "VUSDT"
    VIOLAS_WBTC     = "VWBTC"
    VIOLAS_HBTC     = "VHBTC"
    VIOLAS_WFIL     = "VWFIL"
    BTC_BTC         = "BTC"
    ETHEREUM_USDT   = "usdt"
    ETHEREUM_WBTC   = "wbtc"
    ETHEREUM_HBTC   = "hbtc"
    ETHEREUM_WFIL   = "wfil"

def get_token_name(chain, token):
    return Tokens[f"{chain.upper()}_{token.upper()}"].value

'''
violas or libra client
'''


def get_violasclient(chain = "violas"):
    if chain == "libra":
        return violasproof(name, stmanage.get_libra_nodes(), chain)
    return violasproof(name, stmanage.get_violas_nodes(), chain)

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
        logger.debug(f"ethereum support tokens: {tokens}")
        for token in tokens:
            client.load_contract(token)
    return client
    
def get_ethwallet(chain = "ethereum"):
    return ethwallet(name, dataproof.wallets("ethereum"), chain)

'''
btc client
'''

def get_btcclient():
    return btcclient(name, stmanage.get_btc_conn())

def get_btcwallet():
    return btcwallet(name, dataproof.wallets("btc"))

'''
proof client
'''
def get_proofclient(dtype = "e2vm"):
    return requestclient(name, stmanage.get_db(dtype))

def is_violas_tran_mark(dtype, datas):
    tran_data = json.loads(datas) if isinstance(datas, str) else datas
    data = json.loads(tran_data.get("data", {}))

    return data.get("flag") == "violas" and data.get("type") == f"{dtype}_mark"

def get_tran_id(dtype, datas):
    tran_data = json.loads(datas) if isinstance(datas, str) else datas
    data = json.loads(tran_data.get("data"))
    return data.get("id")

def is_time_in(start_time, max_work_time):
    return start_time + max_work_time >= int(time.time())

def test_e2vm_usdt():
    test_e2vm(Tokens.ETHEREUM_USDT.value, Tokens.VIOLAS_USDT.value)

def test_e2vm_wbtc():
    test_e2vm(Tokens.ETHEREUM_WBTC.value, Tokens.VIOLAS_WBTC.value)

def test_e2vm_hbtc():
    test_e2vm(Tokens.ETHEREUM_HBTC.value, Tokens.VIOLAS_HBTC.value)

def test_e2vm_wfil():
    test_e2vm(Tokens.ETHEREUM_WFIL.value, Tokens.VIOLAS_WFIL.value)

@output_args_func
def test_e2vm(eth_token_name = Tokens.ETHEREUM_USDT.value, violas_token_name = Tokens.VIOLAS_USDT.value):

    ewallet = get_ethwallet()
    eclient = get_ethclient()
    vclient = get_violasclient()
    max_work_time = 360

    #send usdt token, to mapping violas-USDT
    from_address    = stmanage.get_map_address("e2vm", "ethereum")

    #proof contract, recevie approve
    to_address      = eclient.get_proof_contract_address("main").datas

    #will received violas-usdt, and set it to proof's datas
    vls_receiver    = stmanage.get_receiver_address_list("v2em", "violas")[0] #DD user

    #from these address get transaction, checkout exchange-e2vm transaction, get payment amount(usdt)
    vls_e2vm_senders  = stmanage.get_sender_address_list("e2vm", "violas") 


    vclient._logger.debug(f'''
    vls receiver({violas_token_name} payee) = {vls_receiver}
    from address = {from_address}
    to address = {to_address}
    vls_e2vm_senders  = {vls_e2vm_senders}
            ''')

    ret = ewallet.get_account(from_address)
    assert ret.state == error.SUCCEED, f"get account(from_address) failed"
    account = ret.datas

    for token_id in [eth_token_name]:
        if not work_continue():
            break

        start_time = time.time()
        ret = eclient.get_token_min_amount(token_id)
        assert ret.state == error.SUCCEED, f"get {token_id} min amount failed"
        amount = max(2 * eclient.get_decimals(token_id), ret.datas)

        ret = eclient.address_is_exists(from_address)
        assert ret.state == error.SUCCEED, ret.message
        found = ret.datas

        if found:
            ret = eclient.get_address_sequence(from_address)
            assert ret.state == error.SUCCEED, ret.message
            sequence = ret.datas
        else: 
            sequence = -1

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
            if ret.state != error.SUCCEED:
                print(ret.message)
                continue 

            new_sequence = ret.datas
            sleep(2)
            assert is_time_in(start_time, max_work_time), f"time out, {from_address} sequence not changed"
        else:
            print("map proof is saved ethereum.")

        #get transaction info with from_address, sequence
        ret = eclient.get_transaction_version(from_address, new_sequence)
        assert ret.state == error.SUCCEED, ret.message
        version = ret.datas

        #wait state changed, get amount, usdt transfer maybe have transaction fee
        state = "start"
        map_amount = 0 
        while state == "start" and work_continue():
            ret = eclient.get_transactions(version, 1)
            if ret.state != error.SUCCEED:
                print(ret.message)
                continue 

            tran = ret.datas[0]
            state = tran.get_state()
            map_amount = tran.get_amount()
            info = afilter.get_tran_data(tran, False)
            
            message_wheel(start_time, max_work_time, f"check state change, eth proof {version} state not changed, check usdt transaction")
            assert is_time_in(start_time, max_work_time), f"time out, eth proof {version} state not changed, check usdt transaction"


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
                    if ret.state != error.SUCCEED:
                        print(f"get_address_sequence failed. {ret.message}")
                        continue 
                    latest_sequence = ret.datas
                    while (not mapping_ok) and start_sequence <= latest_sequence and work_continue():
                        ret = vclient.get_transaction_version(sender, start_sequence)
                        if ret.state != error.SUCCEED:
                            print(ret.message)
                            continue 

                        new_version = ret.datas

                        ret = vclient.get_transactions(new_version, 1, True)
                        if ret.state != error.SUCCEED:
                            print(ret.message)
                            continue 

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
                        vls_version = info.get("version")

                        message_wheel(start_time, max_work_time, f"violas version = {vls_version} eth tran version = {version} tran_tran_id = {tran_tran_id}  vls_receiver = {vls_receiver} tran_receiver = {tran_receiver}")
                        if vls_receiver == tran_receiver:

                            to_amount = amountconver(map_amount, amountconver.amounttype.ETHEREUM, eclient.get_decimals(eth_token_name)).amount(amountconver.amounttype.VIOLAS, eclient.get_decimals(eth_token_name))
                            assert tran_amount == to_amount, f"mapping amount is error. eth-{token_id} amount = {map_amount}, but violas-{tran_token_id} amount is {tran_amount}, decimals = {eclient.get_decimals(eth_token_name)}"
                            mapping_ok = True
                            print(f'''
                            mapping succeed. 
                            check violas transaction: 
                            violas receiver(payee) = {vls_receiver} 
                            violas version = {new_version} 
                            violas map amount = {tran_amount}({violas_token_name})
                            ethereum version = {version}
                            ethereum sender = {from_address}
                            ethereum send amount: {amount}({eth_token_name}) 
                            ethereum send map amount: {map_amount}({eth_token_name}) 
                            ethereum chain gas = {amount - map_amount}({eth_token_name}) 
                            ''')
                            continue
                        assert is_time_in(start_time, max_work_time),  f"time out, check bridge server is working...tran_tran_id = {tran_tran_id}"

def test_v2em_vusdt():
    test_v2em(map_token_id = Tokens.VIOLAS_USDT.value, eth_token_name = Tokens.ETHEREUM_USDT.value)
    
def test_v2em_vwbtc():
    test_v2em(map_token_id = Tokens.VIOLAS_WBTC.value, eth_token_name = Tokens.ETHEREUM_WBTC.value)

def test_v2em_vhbtc():
    test_v2em(map_token_id = Tokens.VIOLAS_HBTC.value, eth_token_name = Tokens.ETHEREUM_HBTC.value)
    
def test_v2em_vwfil():
    test_v2em(map_token_id = Tokens.VIOLAS_WFIL.value, eth_token_name = Tokens.ETHEREUM_WFIL.value)

@output_args_func
def test_v2em(map_token_id = Tokens.VIOLAS_USDT.value, eth_token_name = Tokens.ETHEREUM_USDT.value):
    ewallet = get_ethwallet()
    eclient = get_ethclient()
    vclient = get_violasclient()
    vwallet = get_violaswallet()
    max_work_time = 180
    map_amount = 2_11_0018

    #received eth-erc20 address(mapping result)
    erc20_receiver = '0xf3FE0CB3b0c8Ab01631971923CEcDd14D857358A'
    
    #from this address send v2em request(violas transaction)
    from_address = stmanage.get_sender_address_list(datatype.E2VM, trantype.VIOLAS)[0]

    #receive v2em request, DD-account
    to_address = stmanage.get_receiver_address_list(datatype.V2EM, trantype.VIOLAS)[0]
    metadata = vclient.create_data_for_start(trantype.VIOLAS, datatype.V2EM, erc20_receiver)

    vclient._logger.debug(f'''
    {eth_token_name} receiver = {erc20_receiver}
    send {eth_token_name} address = {from_address}
    recever mapping receiver = {to_address}
    metadata = {metadata}
    map_amount = {map_amount}
    {eth_token_name} receiver amount: {eclient.get_balance(erc20_receiver, eth_token_name).datas} {eth_token_name}
            ''')
    ret = vwallet.get_account(from_address)
    assert ret.state == error.SUCCEED, f"get {from_address} account failed. {ret.message}"
    map_sender = ret.datas

    before_usdt_amount = eclient.get_balance(erc20_receiver, eth_token_name).datas
    ret = vclient.send_coin(map_sender, to_address, map_amount, map_token_id, data = metadata)
    assert ret.state == error.SUCCEED, f"send coin({map_token_id}) faild from = {from_address} to_address = {to_address} metadata = {metadata}. {ret.message}"
    vclient._logger.debug(f"send coin result: {ret}")

    ret = vclient.get_address_version(from_address)
    txn = ret.datas

    start_time = int(time.time())
    while start_time + max_work_time >= int(time.time()) and work_continue():
        after_usdt_amount = eclient.get_balance(erc20_receiver, eth_token_name).datas
        if after_usdt_amount > before_usdt_amount:
            print(f'''
            mapping ok, 
            mapping to {erc20_receiver} {eth_token_name} 
            eth amount  {after_usdt_amount - before_usdt_amount}{eth_token_name}, 
            input amount is {map_amount}{map_token_id} . 
            check detail of violas {txn}"
            ''')
            return

        message_wheel(max_work_time, start_time, f"v2em verson = {txn}")

    if work_continue():
        assert False, f"time out, check bridge server is working...{txn}"

@output_args_func
def test_b2vm():
    bwallet = get_btcwallet()
    bclient = get_btcclient()
    vclient = get_violasclient()
    vwallet = get_violaswallet()
    max_work_time = 1200

    #violas-BTC : bitcoin-BTC = 1 : 100
    map_amount = 1_0000 #satoshi 1_0000_0000 = 1 BTC
    
    #send BTC from this address
    from_address = '2MyMHV6e4wA2ucV8fFKzXSEFCwrUGr2HEmY'
    assert bwallet.address_is_exists(from_address), f"sender {from_address} is not found in btc wallet"

    #association btc account, receive btc from other btc wallet, only send  btc to this account, can mapping vls-btc
    to_address = stmanage.get_receiver_address_list(datatype.B2VM, trantype.BTC)[0]
    assert bwallet.address_is_exists(to_address), f"association btc account {to_address} is not found in btc wallet"

    #send vls_btc_sender: get transaction(b2vm) from this account, check b2vm is succeed
    vls_btc_sender = stmanage.get_sender_address_list(datatype.B2VM, trantype.VIOLAS)[0]
    found_vbs = vwallet.has_account_by_address(vls_btc_sender).datas
    print(f"found {vls_btc_sender} state : {found_vbs}")
    assert found_vbs == True, f"not found violas chain sender({vls_btc_sender}) of btc token"

    #receive violas-BTC from b2vm: payee   this account is not other payment
    vls_btc_receiver = stmanage.get_receiver_address_list(datatype.V2BM, trantype.VIOLAS)[0]
    found_vbr = vwallet.has_account_by_address(vls_btc_receiver).datas
    assert found_vbr == True, f"not found violas chain receiver({vls_btc_receiver}) of btc token"
    sequence = int(time.time())
    btc_module = "00000000000000000000000000000001"

    auth, to_addr = split_full_address(vls_btc_receiver)
    map_tran_id = f"{to_addr}_{sequence}"
    vclient._logger.debug(f'''
    VBTC receiver = {vls_btc_receiver}
    from address = {from_address}
    to address = {to_address}
    map amount : {map_amount} satoshi == {map_amount / 100} {Tokens.VIOLAS_BTC.value}
    vls_btc_sender  = {vls_btc_sender}
    tran_id ={map_tran_id}
            ''')
    #mark vls-btc-sender current sequence
    ret = vclient.get_address_sequence(vls_btc_sender)
    assert ret.state == error.SUCCEED, ret.message
    sender_start_sequence = ret.datas

    #mark currenct BTC amount
    ret = vclient.get_balance(vls_btc_receiver, Tokens.VIOLAS_BTC.value, None)
    assert ret.state == error.SUCCEED, f"get balance({vls_btc_receiver}, {Tokens.VIOLAS_BTC.value}) failed. {ret.message}"
    before_btc_amount = ret.datas
    vclient._logger.debug(f"{vls_btc_receiver} have {before_btc_amount} {Tokens.VIOLAS_BTC.value}")

    btc_amount = amountconver(map_amount, amountconver.amounttype.BTC).amount(amountconver.amounttype.BTC)
    auth, addr = split_full_address(vls_btc_receiver)
    ret = bclient.sendexproofstart(datatype.B2VM.value, from_address, to_address, btc_amount, addr, sequence, btc_module)
    assert ret.state == error.SUCCEED, f"sendexproofstart failed. {ret.message}"
    txid = ret.datas

    #check btc transaction is in chain
    start_time = int(time.time())
    confirmations = 0
    while start_time + max_work_time >= int(time.time()) and work_continue():
        ret = bclient.call_original_cli("getrawtransaction", txid, True)

        if ret.state != error.SUCCEED:
            message_wheel(max_work_time, start_time)
            continue

        tran_info = ret.datas
        confirmations = tran_info.get("confirmations", 0)
        if confirmations <= 0:
            message_wheel(max_work_time, start_time, f"txid = {txid}, confirmations = {confirmations}")
            continue


    print(f"\nbtc transaction({txid}): confirmations = {confirmations}")
    #will increase btc amount of vls_btc_receiver
    b2vm_amount = amountconver(map_amount, amountconver.amounttype.BTC).microamount(amountconver.amounttype.VIOLAS)
    #wait 30 s, make sure v2bm is exchange, may be check transaction is more acurrate ??????, here is use Ideal state
    start_time = int(time.time())
    while start_time + max_work_time >= int(time.time()) and work_continue():
        #mark vls-btc-sender current sequence
        ret = vclient.get_address_sequence(vls_btc_sender)
        if ret.state != error.SUCCEED:
            continue

        sender_latest_sequence = ret.datas
        if sender_latest_sequence == sender_start_sequence:
            message_wheel(max_work_time, start_time, info = f"vls vbtc sender({vls_btc_sender}) pre sequence = {sender_start_sequence} latest sequence = {sender_latest_sequence}")
            continue

        print(f"\nfound violas account {vls_btc_sender} had new sequence latest sequence {sender_latest_sequence}")
        while sender_start_sequence <= sender_latest_sequence and start_time + max_work_time >= int(time.time()) and work_continue():
            sender_start_sequence += 1
            ret = vclient.get_transaction_version(vls_btc_sender, sender_start_sequence)
            if ret.state != error.SUCCEED:
                print(f"\nget_transaction_version({vls_btc_sender}, {sender_start_sequence}) failed. {ret.message}")
                continue
            new_version = ret.datas

            ret = vclient.get_transactions(new_version, 1, True)
            if ret.state != error.SUCCEED:
                print(f"\nget_transactions({new_version}) failed. {ret.message}")
                continue
            
            tran = ret.datas[0] 
            info = afilter.get_tran_data(tran, "violas")

            if not is_violas_tran_mark("b2vm", info):
                message_wheel(max_work_time, start_time, info = f"not tran mark, check next... (start sequence = (sender_start_sequence) end sequence = {sender_latest_sequence}... {info}")
                continue

            tran_tran_id = get_tran_id("b2vm", info)
            tran_receiver = info.get("receiver")
            tran_sender  = info.get("sender")
            tran_amount = info.get("amount")
            tran_token_id = info.get("token_id")
            
            message_wheel(max_work_time, start_time, info = f"fund transaction ... {info}", sleep_secs = 0)

            if tran_tran_id == map_tran_id:
                assert tran_amount == int(map_amount/100), f"mapping amount is error. eth-{token_id} amount = {map_amount}, but violas-{tran_token_id} amount is {tran_amount}"
                mapping_ok = True
                print(f'''\n
                mapping succeed. 
                check violas address: 
                    version = {new_version}, 
                    receiver = {vls_btc_receiver}, 
                    {Tokens.BTC_BTC.value} amount = {map_amount}"
                    {Tokens.VIOLAS_BTC.value} amount = {tran_amount}"
                    
                ''')
                return

    if work_continue():
        assert False, f"time out, check bridge server is working...{txid}"

@output_args_func
def test_v2bm():
    bwallet = get_btcwallet()
    bclient = get_btcclient()
    vclient = get_violasclient()
    vwallet = get_violaswallet()
    map_token_id = get_token_name("violas", "btc")
    max_work_time = 9000

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

    btc_btc_sender = stmanage.get_sender_address_list(datatype.V2BM, trantype.BTC)[0]
    assert bwallet.address_is_exists(btc_btc_sender), f"sender {btc_btc_sender} is not found in btc wallet"
    before_btc_sender_amount = bclient.get_balance(btc_receiver).datas


    before_btc_amount = bclient.get_balance(btc_receiver).datas
    metadata = vclient.create_data_for_start(trantype.VIOLAS, datatype.V2BM, btc_receiver)
    vclient._logger.debug(f'''
    btc receiver = {btc_receiver}
    send btc address = {from_address}
    recever mapping receiver = to_address
    before amount of btc receiver = {before_btc_amount}
    map amount : {map_amount} {map_token_id} -> {map_amount * 100} BTC
    btc sender({btc_btc_sender}) amount: {int(before_btc_sender_amount * pow(10, 8))} satoshi
    metadata = {metadata}
            ''')

    ret = vwallet.get_account(from_address)
    assert ret.state == error.SUCCEED, f"get {from_address} account failed. {ret.message}"
    map_sender = ret.datas

    ret = vclient.send_coin(map_sender, to_address, map_amount, map_token_id, data = metadata)
    assert ret.state == error.SUCCEED, f"send coin faild from = {from_address} to_address = {to_address} metadata = {metadata}. {ret.message}"
    vclient._logger.debug(f"send coin result: {ret}")

    ret = vclient.get_address_version(from_address)
    txn = ret.datas

    start_time = int(time.time())
    while start_time + max_work_time >= int(time.time()) and work_continue():
        after_btc_amount = bclient.get_balance(btc_receiver).datas
        if after_btc_amount > before_btc_amount:
            after_btc_sender_amount = bclient.get_balance(btc_receiver).datas
            vclient._logger.debug(f'''
            \nmapping ok, 
            mapping to {btc_receiver} amount  {int((after_btc_amount - before_btc_amount) * pow(10, 8))} satoshi, 
            input amount is {map_amount * 100} satoshi 
            current amount {after_btc_amount} BTC ({int(after_btc_amount * pow(10, 8))} satoshi)")
            {btc_btc_sender} satoshi change
                before amount(satoshi) of mapping: {int(before_btc_sender_amount * pow(10, 8))} satoshi
                after amount(satoshi) of mapping: {int(after_btc_sender_amount * pow(10, 8))} satoshi
                gas: {map_amount * 100 - int((after_btc_sender_amount - before_btc_sender_amount) * pow(10, 8))}(satoshi)
            ''')
            return

        message_wheel(max_work_time, start_time, f"v2em verson = {txn}")

    if work_continue():
        assert False, f"time out, check bridge server is working...{txn}"

def message_wheel(max_work_time, start_time, info = "", sleep_secs = 2):   
        print(f"\r\bRemaining time = {max_work_time - int(time.time() - start_time)}(s) will sleeping... {sleep_secs} s, {info}", end = "") 
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

def setup():
    stmanage.set_conf_env("../bvexchange.toml")

    signal.signal(signal.SIGINT, signal_stop)
    signal.signal(signal.SIGTSTP, signal_stop)
    signal.signal(signal.SIGTERM, signal_stop)

if __name__ == "__main__":
    setup()
    pa = parseargs(globals())
    pa.test(sys.argv)


