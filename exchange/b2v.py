#!/usr/bin/python3
import operator
import sys, os
import json
import log
sys.path.append(os.getcwd())
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
from db.dbb2v import dbb2v
from btc.btcclient import btcclient
import vlsopt.violasclient
from vlsopt.violasclient import violasclient, violaswallet
from vlsopt.violasproof import violasproof
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from baseobject import baseobject
from enum import Enum

COINS = comm.values.COINS
#load logging
name="b2v"
wallet_name = "vwallet"

class exb2v(baseobject):
    __warning_count = {}
    __show_warning_count = 1
    def __init__(self, name, vnodes , bnode,  module, combin, chain = "violas"):
        baseobject.__init__(self, name);
        self.set_from_chain("btc")
        self.set_map_chain(chain)
        #btc init
        self._bclient = btcclient(name, bnode)
        self._b2v = dbb2v(self.name(), f"{self.from_chain.()}_{self.name()}.db")
    
        #violas init
        self._vclient = violasproof(self.name(), vnodes)
        self._vwallet = violaswallet(self.name(), wallet_name)
    
        self._module_address = module
        self._combineaddress = combin 

    def append_waning(self, key):
        if key in self.__warning_count:
            self.__warning_count[key] += 1
        else:
            self.__warning_count[key] = 1

    def set_show_warning_count(self, count):
        self.__show_warning_count = count

    def get_show_warning_count(self):
        return self.__show_warning_count

    def can_show_waning(self, key, update = True):
        count = 0
        if key in self.__warning_count:
            count = self.__warning_count[key]
        if update == True:
            self.append_waning(key)
        return count < self.__show_warning_count

    def __merge_proof_to_rpcparams(self, rpcparams, dbinfos):
        try:
            self._logger.debug("start __merge_proof_to_rpcparams")
            for info in dbinfos:
                if info.toaddress in rpcparams.keys():
                    rpcparams[info.toaddress].append({"address":"%s"%(info.vaddress), "sequence":info.sequence})
                else:
                    rpcparams[info.toaddress] = [{"address":"%s"%(info.vaddress), "sequence":info.sequence}]
    
            return result(error.SUCCEED, "", rpcparams)
        except Exception as e:
            ret = parse_except(e)
        return ret
    
    def __get_excluded(self, b2v):
        try:
            rpcparams = {}
            #Proof that integration should be excluded(dbb2v.db)
            ## succeed
            scddatas = b2v.query_b2vinfo_is_succeed()
            if(scddatas.state != error.SUCCEED):
                return scddatas
    
            ret = self.__merge_proof_to_rpcparams(rpcparams, scddatas.datas)
            if(ret.state != error.SUCCEED):
                return ret
            
            ## btcfailed 
            bflddatas = b2v.query_b2vinfo_is_btcfailed()
            if(bflddatas.state != error.SUCCEED):
                return bflddatas
    
            ret = self.__merge_proof_to_rpcparams(rpcparams, bflddatas.datas)
            if(ret.state != error.SUCCEED):
                return ret
    
            ## btcsucceed
            btcscddatas = b2v.query_b2vinfo_is_btcsucceed()
            if(btcscddatas.state != error.SUCCEED):
                return bflddatas
    
            ret = self.__merge_proof_to_rpcparams(rpcparams, btcscddatas.datas)
            if(ret.state != error.SUCCEED):
                return ret
    
            ret = result(error.SUCCEED, "", rpcparams)
        except Exception as e:
            ret = parse_except(e)
        return ret
    
    def __checks(self):
        assert (len(stmanage.get_btc_conn()) == 4), "btc_conn is invalid."
        assert (len(stmanage.get_sender_address_list(self.name(), self.map_chain())) > 0 ), "violas sender not found."
        for addr in stmanage.get_sender_address_list(self.name(), self.map_chain()):
            assert len(addr) == 64, f"violas address({addr}) is invalid."

        assert (len(stmanage.get_receiver_address_list(self.name(), self.from_chain())) > 0 ), "btc receiver not found."
        for addr in stmanage.get_receiver_address_list(self.name(), self.from_chain()):
            assert len(addr) >= 20, f"btc address({addr}) is invalid."
    
        assert (len(stmanage.get_module_address(self.name(), self.map_chain())) == 64), "module_address is invalid"
        assert (len(stmanage.get_violas_nodes()) > 0), "violas_nodes is invalid."
    
    def __hasplatformbalance(self, vclient, address, vamount = 0):
        try:
            ret = vclient.get_platform_balance(address)
            if ret.state != error.SUCCEED:
                return ret
    
            self._logger.debug(f"platform balance {ret.datas}")
            balance = ret.datas
            if balance >= vamount:
                ret = result(error.SUCCEED, "", True)
            else:
                ret = result(error.SUCCEED, "", False)
        except Exception as e:
            ret = parse_except(e)
        return ret
    
    def __hasviolasbalance(self, vclient, address, module, vamount):
        try:
            ret = vclient.get_violas_balance(address, module)
            if ret.state != error.SUCCEED:
                return ret
    
            self._logger.debug(f"violas coin balance {ret.datas}")
            balance = ret.datas
            if balance >= vamount:
                ret = result(error.SUCCEED, "", True)
            else:
                ret = result(error.SUCCEED, "", False)
        except Exception as e:
            ret = parse_except(e)
        return ret
    
    def __update_db_btcsucceed_to_complete(self, bclient, b2v):
        ##search db state is succeed
        try:
            scddatas = b2v.query_b2vinfo_is_btcsucceed()
            if scddatas.state != error.SUCCEED:
                self._logger.error("db error")
                return result(error.FAILED)
    
            ##excluded btc blockchain state is not start,update dbb2v state to complete
            ##dbb2v state is complete, that means  btc blockchain state is cancel or succeed
            for row in scddatas.datas:
                vaddress  = row.vaddress
                sequence = row.sequence
                ret = bclient.isexproofcomplete(vaddress, sequence)
                if(ret.state == error.SUCCEED and ret.datas["result"] == "true"):
                    ret = b2v.update_b2vinfo_to_complete_commit(vaddress, sequence)
    
            ret = result(error.SUCCEED)
        except exception as e:
            ret = parse_except(e)
        return ret
    
    def __rechange_btcstate_to_end_from_btcfailed(self, bclient, b2v, combineaddress, module_address, receivers):
        try:
            self._logger.debug(f"start __rechange_btcstate_to_end_from_btcfailed(combineaddress={combineaddress}, module_address={module_address}, receivers={receivers})")
            bflddatas = b2v.query_b2vinfo_is_btcfailed()
            if(bflddatas.state != error.SUCCEED):
                return bflddatas
    
            for data in bflddatas.datas:
                receiver = data.toaddress
                if module_address != data.vtoken:
                    self._logger.warning(f"db's vtoken({data.vtoken}) not match module_address({module_address}), ignore it, next")
                    continue
    
                if receiver not in receivers:
                    self._logger.warning(f"db's fromaddress({data.fromaddress}) not match btc_recivers({receivers}), ignore it, next")
                    continue
    
                vaddress = data.vaddress
                bamount = data.bamount  
                sequence = data.sequence
                height = data.height
    
                #recheck b2v state in blockchain, may be performed manually
                ret = bclient.isexproofcomplete(vaddress, sequence)
                if(ret.state == error.SUCCEED and ret.datas["result"] == "true"):
                    ret = b2v.update_b2vinfo_to_complete_commit(vaddress, sequence)
                    continue
    
                #The receiver of the start state can change the state to end
                ret = bclient.sendexproofend(receiver, combineaddress, vaddress, sequence, float(bamount)/COINS, height)
                if ret.state != error.SUCCEED:
                    ret = b2v.update_b2vinfo_to_btcfailed_commit(vaddress, sequence)
                    assert (ret.state == error.SUCCEED), "db error"
                else:
                    ret = b2v.update_b2vinfo_to_btcsucceed_commit(vaddress, sequence, ret.datas)
                    assert (ret.state == error.SUCCEED), "db error"
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret
    
    def __get_violas_sender(self, vclient, vwallet, module, vamount, min_gas):
        for sender in stmanage.get_sender_address_list(self.name(), self.map_chain()):
            ret = vwallet.get_account(sender)
            if ret.state != error.SUCCEED:
                continue
            asender = ret.datas
    
            #make sure sender address is binded module
            ret = vclient.account_has_violas_module(sender, module)
            if ret.state != error.SUCCEED:
                self._logger.warning("violas client error, next ...")
                continue
    
            if ret.datas != True:
                self._logger.warning(f"sender account {sender} not bind module {module}. next ...")
                continue
    
            #make sure sender address has enough platform coins
            ret = self.__hasplatformbalance(vclient, sender, min_gas)
            if ret.state != error.SUCCEED:
                continue
    
            if ret.datas != True:
                self._logger.warning(f"{sender} not enough platform coins {min_gas}, next ...")
                continue
    
            #make sure sender address has enough violas coins
            ret = self.__hasviolasbalance(vclient, sender, module, vamount)
            if ret.state != error.SUCCEED:
                continue
    
            if ret.datas != True:
                self._logger.warning(f"{sender} not enough {module} coins {vamount}, next ...")
                continue
            return result(error.SUCCEED, "", (asender, sender))
    
        return result(error.FAILED, "not found conform sender from wallet, check balance")
    
    
    def stop(self):
        self._vclient.stop()
        self.work_stop()
        

    def start(self):
        try:
            self._logger.debug("start b2v work")
    
            #requirement checks
            self.__checks()
    
            #btc init
            bclient = self._bclient
            b2v = self._b2v
    
            #violas init
            vclient = self._vclient
            vwallet = self._vwallet
    
            module_address = self._module_address
            combineaddress = self._combineaddress
    
            #update db state by proof state
            ret = self.__update_db_btcsucceed_to_complete(bclient, b2v)
            if ret.state != error.SUCCEED:
                return ret
    
            #update proof state to end, and update db state, prevstate is btcfailed in db. 
            #When this happens, there is not enough Bitcoin, etc.
            self.__rechange_btcstate_to_end_from_btcfailed(bclient, b2v, combineaddress, module_address, stmanage.get_receiver_address_list(self.name(), self.map_chain()))
    
            #get all excluded info from db
            rpcparams = {}
            ret = self.__get_excluded(b2v)
            if ret.state != error.SUCCEED:
                self._logger.error("db error")
                return result(error.FAILED)
    
            rpcparams = ret.datas
            min_gas = comm.values.MIN_EST_GAS 
    
            #set receiver: get it from stmanage or get it from blockchain
            receivers = list(set(stmanage.get_receiver_address_list(self.name(), self.from_chain())))
    
            #modulti receiver, one-by-one
            for receiver in receivers:
                if not self.work():
                    break

                #check receiver is included in wallet
                ret = bclient.has_btc_banlance(receiver, 0)
                if ret.state != error.SUCCEED or ret.datas != True:
                    self._logger.warning(f"receiver({receiver}) has't enough satoshi ({comm.values.MIN_EST_GAS}). ignore it's b2v, next receiver.")
                    continue 
    
                excluded = []
                if receiver in rpcparams:
                    excluded = rpcparams[receiver]
    
                self._logger.debug(f"check receiver={receiver} excluded={excluded}")
                ret = bclient.listexproofforstart(receiver, excluded)
                if ret.state == error.SUCCEED and len(ret.datas) > 0:
                    for data in ret.datas:
                        if not self.work():
                            break

                        #grant vbtc 
                        ##check 
                        to_address = data["address"]
                        sequence = int(data["sequence"])
                        to_module_address = data["vtoken"]
                        vamount = int(float(data["amount"]) * COINS)
                        if (len(module_address) != 64 or module_address != to_module_address):
                            if self.can_show_waning(f"vtoken is invalid{to_address}.{sequence}"):
                               self._logger.warning(f"vtoken({to_module_address}) is invalid.(to_address:{to_address} sequence:{sequence}")
                            continue
    
                        if vamount <= 0:
                            self._logger.warning(f"amount({vamount}) is invalid.(to_address:{to_address} sequence:{sequence}")
                            continue
                        
                        #get sender account and address
                        ret = self.__get_violas_sender(vclient, vwallet, to_module_address, vamount, min_gas)
                        if ret.state != error.SUCCEED:
                            self._logger.debug(f"get account failed. {ret.message}")
                            continue
    
                        #violas sender, grant vbtc
                        vsender  = ret.datas[0]
                        vsender_address = ret.datas[1]
                                    #make sure receiver address is binded module
                        ret = vclient.account_has_violas_module(to_address, to_module_address)
                        if ret.state != error.SUCCEED:
                            continue
    
                        if ret.datas != True:
                            self._logger.warning(f"account {to_address} not bind module {to_module_address}")
                            continue
                           
                        self._logger.info(f"start new btc -> vbtc(address={to_address}, sequence={int(data['sequence'])}, amount={vamount}, module={to_module_address}")
                        ##send vbtc to vaddress, vtoken and amount
                        tran_data = vclient.create_data_for_mark(self.map_chain(), self.name(), data["txid"], int(data["sequence"]))
                        ret = vclient.send_violas_coin(vsender, to_address, vamount, to_module_address, data=tran_data)
                        if ret.state != error.SUCCEED:
                            continue
                        
                        ##create new row to db. state = start 
                        ret = b2v.has_b2vinfo(data["address"], data["sequence"])
                        assert (ret.state == error.SUCCEED), "db error"
    
                        if ret.datas == False:
                            ret = b2v.insert_b2vinfo_commit(data["txid"], data["issuer"], data["receiver"], int(float(data["amount"]) * COINS), 
                                    data["address"], int(data["sequence"]), int(float(data["amount"]) * COINS), data["vtoken"], data["creation_block"], data["update_block"])
                            assert (ret.state == error.SUCCEED), "db error"
    
                        rettmp = vclient.get_address_version(vsender_address)
                        height = -1
                        ##update db 
                        ###succeed:dbb2v state = succeed
                        if rettmp.state == error.SUCCEED:
                            height =  rettmp.datas
                            ret =b2v.update_b2vinfo_to_succeed_commit(data["address"], int(data["sequence"]), height)
                            assert (ret.state == error.SUCCEED), "db error"
                        
                        #The receiver of the start state can change the state to end
                        ret = bclient.sendexproofend(receiver, combineaddress, data["address"], int(data["sequence"]), float(vamount)/COINS, height)
                        if ret.state != error.SUCCEED:
                            ret = b2v.update_b2vinfo_to_btcfailed_commit(data["address"], int(data["sequence"]))
                            assert (ret.state == error.SUCCEED), "db error"
                        else:
                            ret = b2v.update_b2vinfo_to_btcsucceed_commit(data["address"], int(data["sequence"]), ret.datas)
                            assert (ret.state == error.SUCCEED), "db error"
    
            ret = result(error.SUCCEED) 
    
        except Exception as e:
            ret = parse_except(e)
        finally:
            
            #vclient.disconn_node()
            #vwallet.dump_wallet()
            self._logger.debug("works end.")
    
        return ret
    
