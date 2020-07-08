#!/usr/bin/python3
# coding default python2.x : ascii   python3.x :UTF-8
# -*- coding: UTF-8 -*-
'''
btc and vbtc exchange main
'''
import operator
import signal
import sys, os
import traceback
import log
import log.logger
import threading
from time import sleep, ctime
import stmanage
import subprocess
import comm.functions as fn
from exchange import b2v, v2b, exlv
from comm.result import parse_except
from analysis import analysis_base, analysis_filter, analysis_proof
from enum import Enum
from comm.values import workmod as work_mod

name="bvexchange"

class works:
    __threads = []
    __work_looping = {}
    __work_obj = {}
    __record_db = "record"

    __libra_min_valid_version   = 1952696
    __violas_min_valid_version  = 1413729
    __btc_min_valid_version     = 0
    def __init__(self):
        logger.debug("works __init__")
        self.__funcs_map = {}
        self.init_func_map()
        for mod in self.__work_looping:
            self.__work_looping[mod.name] = 1

        self.__threads = []

    def __del__(self):
        del self.__threads

    def record_db_name(self):
        return self.__record_db
    
    def set_work_obj(self, obj):
        old_obj = self.__work_obj.get(obj.name())
        if old_obj is not None:
            del old_obj

        if obj.name() in self.__work_obj:
            del self.__work_obj[obj.name()]

        self.__work_obj[obj.name()] = obj

    def work_b2v(self, **kargs):
        try:
            logger.critical("start: b2vxxx")
            nsec = kargs.get("nsec", 0)
            mod = kargs.get("mod")
            assert mod is not None, f"mod name is None"
            dtype = self.get_dtype_from_mod(mod)
            while (self.__work_looping.get(mod, False)):
                logger.debug(f"looping: {mod}")
                try:
                    chain = "violas"
                    obj = b2v.exb2v(mod,
                            stmanage.get_violas_nodes(), 
                            stmanage.get_btc_conn(), 
                            stmanage.get_module_address(dtype, chain), 
                            stmanage.get_token_id(dtype, chain), 
                            stmanage.get_combine_address(), 
                            chain=chain)
                    self.set_work_obj(obj)
                    obj.start()
                except Exception as e:
                    parse_except(e)
                sleep(nsec)
        except Exception as e:
            parse_except(e)
        finally:
            logger.critical("stop: b2v")

    def work_v2b(self, **kargs):
        try:
            logger.critical("start: v2b")
            nsec = kargs.get("nsec", 0)
            mod = kargs.get("mod")
            assert mod is not None, f"mod name is None"
            dtype = self.get_dtype_from_mod(mod)
            while (self.__work_looping.get(mod, False)):
                logger.debug(f"looping: {mod}")
                chain = "violas"
                try:
                    obj = v2b.exv2b(mod, 
                            stmanage.get_violas_nodes(), 
                            stmanage.get_btc_conn(), 
                            stmanage.get_db(dtype), 
                            stmanage.get_module_address(dtype, chain), 
                            stmanage.get_token_id(dtype, chain), 
                            list(set(stmanage.get_receiver_address_list(dtype, chain))),
                            chain=chain)
                    self.set_work_obj(obj)
                    obj.start()
                except Exception as e:
                    parse_except(e)
                sleep(nsec)
        except Exception as e:
            parse_except(e)
        finally:
            logger.critical("stop: v2b")

    def work_vfilter(self, **kargs):
        try:
            logger.critical("start: violas filter")
            nsec = kargs.get("nsec", 0)
            mod = kargs.get("mod")
            assert mod is not None, f"mod name is None"
            dtype = self.get_dtype_from_mod(mod)
            while (self.__work_looping.get(mod, False)):
                logger.debug(f"looping: {mod}")
                try:
                    obj = analysis_filter.afilter(name=mod, ttype="violas", \
                            dbconf=stmanage.get_db(dtype), nodes=stmanage.get_violas_nodes(), chain="violas")
                    obj.set_step(stmanage.get_db(dtype).get("step", 1000))
                    obj.set_min_valid_version(self.__violas_min_valid_version - 1)
                    self.set_work_obj(obj)
                    obj.start()
                except Exception as e:
                    parse_except(e)
                sleep(nsec)
        except Exception as e:
            parse_except(e)
        finally:
            logger.critical("stop: vfilter")

    def work_v2bproof(self, **kargs):
        try:
            logger.critical("start: violas v2b proof")
            nsec = kargs.get("nsec", 0)
            mod = kargs.get("mod")
            assert mod is not None, f"mod name is None"

            #violas transaction's data types 
            dtype = self.get_dtype_from_mod(mod)
            while (self.__work_looping.get(mod, False)):
                logger.debug(f"looping: {mod}")
                try:
                    basedata = "vfilter"
                    obj = analysis_proof.aproof(name=mod, ttype="violas", dtype=dtype, \
                            dbconf=stmanage.get_db(dtype), fdbconf=stmanage.get_db(basedata))
                    obj.append_token_id(dtype, stmanage.get_token_id(dtype, "violas"))
                    obj.set_record(stmanage.get_db(self.record_db_name()))
                    obj.set_step(stmanage.get_db(dtype).get("step", 100))
                    obj.set_min_valid_version(self.__violas_min_valid_version - 1)
                    self.set_work_obj(obj)
                    obj.start()
                except Exception as e:
                    parse_except(e)
                sleep(nsec)
        except Exception as e:
            parse_except(e)
        finally:
            logger.critical("stop: v2bproof")

    def work_lfilter(self, **kargs):
        try:
            logger.critical("start: libra filter")
            nsec = kargs.get("nsec", 0)
            mod = kargs.get("mod")
            assert mod is not None, f"mod name is None"

            dtype = self.get_dtype_from_mod(mod)
            while (self.__work_looping.get(mod, False)):
                logger.debug(f"looping: {mod}")
                try:
                    obj = analysis_filter.afilter(name=mod, ttype="libra", \
                            dbconf=stmanage.get_db(dtype), nodes=stmanage.get_libra_nodes(), chain="libra")
                    obj.set_step(stmanage.get_db(dtype).get("step", 1000))
                    obj.set_min_valid_version(self.__libra_min_valid_version - 1)
                    self.set_work_obj(obj)
                    obj.start()
                except Exception as e:
                    parse_except(e)
                sleep(nsec)
        except Exception as e:
            parse_except(e)
        finally:
            logger.critical("stop: lfilter")

    def work_l2vproof(self, **kargs):
        try:
            logger.critical("start: l2v proof")
            nsec = kargs.get("nsec", 0)
            mod = kargs.get("mod")
            assert mod is not None, f"mod name is None"

            dtype = self.get_dtype_from_mod(mod)
            while (self.__work_looping.get(mod, False)):
                logger.debug(f"looping: {mod}")
                try:
                    basedata = "lfilter"
                    obj = analysis_proof.aproof(name=mod, ttype="libra", dtype=dtype, \
                            dbconf=stmanage.get_db(dtype), fdbconf=stmanage.get_db(basedata))
                    obj.set_record(stmanage.get_db(self.record_db_name()))
                    obj.set_step(stmanage.get_db(dtype).get("step", 100))
                    obj.set_min_valid_version(self.__libra_min_valid_version - 1)
                    self.set_work_obj(obj)
                    obj.start()
                except Exception as e:
                    parse_except(e)
                sleep(nsec)
        except Exception as e:
            parse_except(e)
        finally:
            logger.critical("stop: l2vproof")

    def work_v2lproof(self, **kargs):
        try:
            logger.critical("start: violas v2l proof")
            nsec = kargs.get("nsec", 0)
            mod = kargs.get("mod")
            assert mod is not None, f"mod name is None"

            dtype = self.get_dtype_from_mod(mod)
            while (self.__work_looping.get(mod, False)):
                logger.debug(f"looping: {mod}")
                try:
                    basedata = "vfilter"
                    obj = analysis_proof.aproof(name=mod, ttype="violas", dtype=dtype, \
                            dbconf=stmanage.get_db(dtype), fdbconf=stmanage.get_db(basedata))
                    obj.append_token_id(stmanage.get_support_token_id("violas"))
                    obj.set_record(stmanage.get_db(self.record_db_name()))
                    obj.set_step(stmanage.get_db(dtype).get("step", 100))
                    obj.set_min_valid_version(self.__violas_min_valid_version - 1)
                    self.set_work_obj(obj)
                    obj.start()
                except Exception as e:
                    parse_except(e)
                sleep(nsec)
        except Exception as e:
            parse_except(e)
        finally:
            logger.critical("stop: v2lproof")

    def work_l2v(self, **kargs):
        try:
            logger.critical("start: l2v")
            nsec = kargs.get("nsec", 0)
            mod = kargs.get("mod")
            assert mod is not None, f"mod name is None"

            #libra transaction's data types 
            dtype = self.get_dtype_from_mod(mod)
            while (self.__work_looping.get(mod, False)):
                logger.debug(f"looping: {mod}")
                try:
                    obj = exlv.exlv(mod, 
                            stmanage.get_libra_nodes(),
                            stmanage.get_violas_nodes(), 
                            stmanage.get_db(dtype), 
                            None, #from libra module is fixed
                            None, #libra no token_id
                            stmanage.get_module_address(dtype, "violas", False), 
                            stmanage.get_token_id(dtype, "violas"),
                            list(set(stmanage.get_receiver_address_list(dtype, "libra", False))),
                            list(set(stmanage.get_sender_address_list(dtype, "violas", False))),
                            "libra",
                            "violas")
                    self.set_work_obj(obj)
                    obj.start()
                except Exception as e:
                    parse_except(e)
                sleep(nsec)
        except Exception as e:
            parse_except(e)
        finally:
            logger.critical("stop: l2v")

    def work_v2l(self, **kargs):
        try:
            logger.critical("start: v2l")
            nsec = kargs.get("nsec", 0)
            mod = kargs.get("mod")
            assert mod is not None, f"mod name is None"

            #libra transaction's data types 
            dtype = self.get_dtype_from_mod(mod)
            while (self.__work_looping.get(mod, False)):
                logger.debug(f"looping: {mod}")
                try:
                    obj = exlv.exlv(mod, 
                            dtype,
                            stmanage.get_violas_nodes(), 
                            stmanage.get_libra_nodes(),
                            stmanage.get_db(dtype), 
                            list(set(stmanage.get_receiver_address_list(dtype, "violas", False))),
                            list(set(stmanage.get_sender_address_list(dtype, "libra", False))),
                            stmanage.get_combine_address(dtype, "violas")
                            )
                    self.set_work_obj(obj)
                    obj.start()
                except Exception as e:
                    parse_except(e)
                sleep(nsec)
        except Exception as e:
            parse_except(e)
        finally:
            logger.critical("stop: v2l")

    def work_bfilter(self, **kargs):
        try:
            logger.critical("start: btc filter")
            nsec = kargs.get("nsec", 0)
            mod = kargs.get("mod")
            assert mod is not None, f"mod name is None"

            #libra transaction's data types 
            dtype = self.get_dtype_from_mod(mod)
            while (self.__work_looping.get(mod, False)):
                logger.debug(f"looping: {mod}")
                try:
                    dtype = "bfilter"
                    obj = analysis_filter.afilter(name=mod, ttype="btc", \
                            dbconf=stmanage.get_db(dtype), nodes=stmanage.get_btc_conn(), chain="btc")
                    obj.set_step(stmanage.get_db(dtype).get("step", 1000))
                    obj.set_min_valid_version(self.__btc_min_valid_version - 1)
                    self.set_work_obj(obj)
                    obj.start()
                except Exception as e:
                    parse_except(e)
                sleep(nsec)
        except Exception as e:
            parse_except(e)
        finally:
            logger.critical("stop: bfilter")

    def work_b2vproof(self, **kargs):
        try:
            logger.critical("start: btc b2v proof")
            nsec = kargs.get("nsec", 0)
            mod = kargs.get("mod")
            assert mod is not None, f"mod name is None"

            #libra transaction's data types 
            dtype = self.get_dtype_from_mod(mod)
            while (self.__work_looping.get(mod, False)):
                logger.debug("looping: b2vproof")
                try:
                    basedata = "bfilter"
                    obj = analysis_proof.aproof(name=mod, ttype="btc", dtype=dtype, \
                            dbconf=stmanage.get_db(dtype), fdbconf=stmanage.get_db(basedata))
                    obj.append_module(dtype, stmanage.get_module_address(dtype, "btc", False))
                    obj.set_record(stmanage.get_db(self.record_db_name()))
                    obj.set_step(stmanage.get_db(dtype).get("step", 100))
                    obj.set_min_valid_version(self.__btc_min_valid_version - 1)
                    self.set_work_obj(obj)
                    obj.start()
                except Exception as e:
                    parse_except(e)
                sleep(nsec)
        except Exception as e:
            parse_except(e)
        finally:
            logger.critical("stop: v2lproof")

    def work_comm(self, **kargs):
        try:
            logger.critical("start: comm")
            nsec = kargs.get("nsec", 0)
            mod = kargs.get("mod")
            assert mod is not None, f"mod name is None"

            while(self.__work_looping.get(mod, False)):
                logger.debug("looping: comm")
                sleep(nsec)
        except Exception as e:
            parse_except(e)
        finally:
            logger.critical("stop: comm")

    class work_thread(threading.Thread):
        __name = ""
        __threadId = 0
        __nsec = 1
        __work = ""
        def __init__(self, work, threadId, name, **kargs):
            logger.debug(f"work thread __init__(work_funcs = {work.__name__} threadId = {threadId} name = {name}  kargs = {kargs})")
            threading.Thread.__init__(self)
            self.__threadId = threadId
            self.__name = name
            self.__kargs = kargs
            self.__work = work

        def run(self):
            logger.debug(f"work thread run{self.__kargs}")
            self.__work(**self.__kargs)

    def get_dtype_from_mod(self, modname):
        dtype = modname.lower()
        if dtype[:3] in ["v2b", "b2v", "l2v", "v2l"]:
            if dtype.endswith("ex"):
                return dtype[:-2]
            elif dtype.endswith("proof"):
                return dtype[:-5]
        return dtype

    def thread_append(self, work, mod):
        try:
            obj = self.work_thread(work, mod.value, mod.name.lower(), \
                    nsec = stmanage.get_looping_sleep(mod.name.lower()), \
                    mod = mod.name.lower())
            self.__threads.append(obj)
        except Exception as e:
            parse_except(e)
        finally:
            logger.debug("thread_append")

    def create_func_dict(self, mod, func):
        return {mod.name.lower() : func}

    @property
    def funcs_map(self):
        return self.__funcs_map

    def init_func_map(self):
        self.__funcs_map = {}
        #append proof
        for item in work_mod:
            name = item.name
            if name == "VFILTER":
                self.__funcs_map.update(self.create_func_dict(item, self.work_vfilter))
            elif name == "LFILTER":
                self.__funcs_map.update(self.create_func_dict(item, self.work_lfilter))
            elif name == "BFILTER":
                self.__funcs_map.update(self.create_func_dict(item, self.work_bfilter))
            elif name == "V2BPROOF":
                self.funcs_map.update(self.create_func_dict(item, self.work_v2bproof))
            elif name.startswith("V2L") and len(name) == 11 and name.endswith("PROOF"):
                self.funcs_map.update(self.create_func_dict(item, self.work_v2lproof))
            elif name.startswith("L2V") and len(name) == 11 and name.endswith("PROOF"):
                self.funcs_map.update(self.create_func_dict(item, self.work_l2vproof))
            elif name.startswith("B2V") and len(name) == 8 and name.endswith("PROOF"):
                self.funcs_map.update(self.create_func_dict(item, self.work_b2vproof))
            elif name.startswith("V2B") and len(name) == 8 and name.endswith("PROOF"):
                self.funcs_map.update(self.create_func_dict(item, self.work_v2bproof))
            elif name.startswith("L2V") and len(name) == 8 and name.endswith("EX"):
                self.funcs_map.update(self.create_func_dict(item, self.work_l2v))
            elif name.startswith("V2L") and len(name) == 8 and name.endswith("EX"):
                self.funcs_map.update(self.create_func_dict(item, self.work_v2l))
            elif name.startswith("B2V") and name.endswith("EX"):
                self.__funcs_map.update(self.create_func_dict(item, self.work_b2v))
            elif name.startswith("V2B") and name.endswith("EX"):
                self.__funcs_map.update(self.create_func_dict(item, self.work_v2b))
            elif name == "COMM":
                self.__funcs_map.update(self.create_func_dict(item, self.work_comm))
            else:
                logger.warning(f"not matched function:{item}")

    def start(self, work_mods):
        try:
            logger.debug("start works")

            self.__work_looping = work_mods

            for name, state in work_mods.items():
                if state:
                    self.thread_append(self.funcs_map[name.lower()], work_mod[name.upper()])

            for work in self.__threads:
                work.start() #start work

        except Exception as e:
            parse_except(e)
        finally:
            logger.debug("start end")

    def join(self):
        try:
            logger.debug("start join")

            for work in self.__threads:
                work.join() # work finish
        except Exception as e:
            parse_except(e)
        finally:
            logger.critical("end join")

    def stop(self):
        logger.debug("stop works")
        for mod in self.__work_looping.keys():
            self.__work_looping[mod] = False

        for key in self.__work_obj:
            obj = self.__work_obj.get(key)
            if obj is not None:
                obj.stop()


logger = log.logger.getLogger(name)
work_manage = works()
def signal_stop(signal, frame):
    try:
        logger.debug("start signal : %i", signal )
        global work_manage
        work_manage.stop()
    except Exception as e:
        parse_except(e)
    finally:
        logger.debug("end signal")

def list_valid_mods():
    valid_mods = ["all"]
    for mod in work_mod:
        valid_mods.append(mod.name.lower())
    return valid_mods

def run(mods):
    stmanage.reset()
    
    valid_mods = list_valid_mods()
    for mod in mods:
        if mod is None or mod not in valid_mods:
            raise Exception(f"mod({mod}) is invalid {valid_mods}.")

    #fn.checkrerun(__file__)
    fn.write_pid(name)
    lockpid = fn.filelock(name)
    if lockpid.lock() == False:
        logger.warning("already running.")
        sys.exit(0)

    global work_manage
    logger.debug("start main")
    
    signal.signal(signal.SIGINT, signal_stop)
    signal.signal(signal.SIGTSTP, signal_stop)
    signal.signal(signal.SIGTERM, signal_stop)
    work_mods = {}
    for mod in mods:
        work_mods[mod.lower()] = True
        if mod == "all":
            for wm in work_mod:
                work_mods[wm.name.lower()] = True
            break

    logger.critical(f"work_mods= {work_mods}")
    work_manage.start(work_mods)
    work_manage.join()

def main(argc, argv):
    try:
        if argc < 1:
             raise Exception(f"argument is invalid")
        run(argv)
    except Exception as e:
        parse_except(e)
    finally:
        logger.critical("main end")

if __name__ == '__main__':
    main(len(sys.argv) - 1, sys.argv[1:])
