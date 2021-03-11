#!/usr/bin/python3
from flask import Flask , url_for, request
from markupsafe import escape
app = Flask(__name__)

import operator
import sys, os, time
import json
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
import comm.values
from comm.result import result, parse_except
from comm.error import error
from btc.btcclient import btcclient
from vlsopt.violasclient import violasclient, violaswallet, violasserver
from vlsopt.violasproof import violasproof
from ethopt.ethclient import ethclient, ethwallet
from baseobject import baseobject
from enum import Enum
from flask import render_template

#module self.name
name="faucet"
@app.route('/')
def main():
    try:
        args    = request.args
        token   = args.get("token", "usdt")
        receiver = args.get("receiver")

        print(f"receier = {receiver}")
        if receiver:
            return mint_eth_coin(token, receiver)
        else:
            raise Exception(f"receiver:{receiver} is invalid.")
    except Exception as e:
        ret = parse_except(e)
    return ret.to_json()


def get_ethclient(token = "usdt", chain = "ethereum"):

    client = ethclient(name, stmanage.get_eth_nodes(), chain)
    client.load_vlsmproof(stmanage.get_eth_token("vlsmproof")["address"])
    tokens = client.get_token_list().datas
    print(token)
    print(tokens)
    if token in tokens:
        client.load_contract(token)
    else:
        raise Exception(f"not found token({token})")
    return client
    
def get_ethwallet():
    return ethwallet(name, "faucet_wallet_eth.wlt", "ethereum")

receiver_wait = {}
def mint_eth_coin(token_id, receiver, amount = 100):

    global receiver_wait
    faucet_address = "0x9382690D0B835b69FD9C0bc23EB772a0Ddb3613F"
    now = int(time.time())
    wait = 60

    #wait diff
    diff = int(time.time()) - wait - receiver_wait.get(receiver, 0)
    #if diff < 0: return result(error.FAILED, f"wait {0 - diff}s").to_json()
    receiver_wait.update({receiver: now})

    wallet = get_ethwallet()
    client = get_ethclient(token_id)
    decimals = client.get_decimals(token_id)

    ret = client.get_balance(faucet_address, token_id, None)
    if amount * decimals < amount * decimals:
        ret.message = f"faucet account amount: {ret.datas / decimals}({token_id})"
        ret.state = error.FAILED
        return ret.to_json()


    ret = wallet.get_account(faucet_address)
    print(f"send from {ret.datas.address}")

    if ret.state != error.SUCCEED:
        raise Exception("get account failed")
    account = ret.datas

    ret = client.send_coin_erc20(account, receiver, amount * decimals, token_id)
    assert ret.state == error.SUCCEED, ret.message
    message = ret.message
    

    ret = client.get_balance(receiver, token_id, None)
    current_amount = ret.datas
    ret = client.get_balance(faucet_address, token_id, None)
    faucet_amount = ret.datas
    return {
            "token_id" : token_id, 
            "curent_amount":current_amount / decimals,
            "faucet_amount":faucet_amount / decimals,
            "chain_id":stmanage.get_chain_id(),
            "state": "SUCCEED",
            "message" : message
            }


def mint_diem_coin(amount, currency_code, auth_key, return_txns = True, is_designated_dealer = True):
    #curl -X POST http://faucet.testnet.diem.com/mint\?amount\=1000000\&currency_code\=XUS\&auth_key\=459c77a38803bd53f3adee52703810e3a74fd7c46952c497e75afb0a7932586d\&return_txns\=true
    return_txns = "true" if return_txns else "false" 
    is_designated_dealer = "true" if is_designated_dealer else "false"
    url = f"http://faucet.testnet.diem.com/mint?amount={amount}&currency_code={currency_code}&auth_key={auth_key}&return_txns={return_txns}&is_designated_dealer={is_designated_dealer}"
    response = requests.get(url)
    if response is not None:
        jret = json.loads(response.text)
        return {
                "state": "SUCCEED",
                "message": jret["message"]
                }
    return {"state": "FAILED"}

@app.route("/faucet/", methods = ['GET','POST'])
def faucet():
    show_request()
    address = ""
    message = "here show message"
    ret = {"state" : "SUCCEED", "message": message}
    if request.method == "POST":

        stmanage.set_conf_env("../bvexchange.toml")
        address = request.form['address']
        ret = mint_eth_coin("usdt", address)
    return render_template("index.html", address = address, ret = ret)

with app.test_request_context() as trc:
    print(url_for("faucet"))

def show_request():
    print(f'''
    url_root: {request.url_root}
    args    : {request.args}
          ''')

if __name__ == "__main__":
    from werkzeug.contrib.fixers import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.run()
