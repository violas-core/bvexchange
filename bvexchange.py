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
from exchange import b2v, v2b, v2l, l2v, v2lm, l2vm, v2bm
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

    __libra_min_valid_version   = 0
    __violas_min_valid_version  = 1971_1311
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
                    obj = b2v.b2v(mod,
                            dtype,
                            stmanage.get_btc_nodes(), 
                            stmanage.get_violas_nodes(),
                            stmanage.get_db(dtype), 
                            list(set(stmanage.get_receiver_address_list(dtype, "btc", False))),
                            list(set(stmanage.get_sender_address_list(dtype, "violas", False))),
                            stmanage.get_combine_address(dtype, "btc", True),
                            stmanage.get_swap_module(),
                            stmanage.get_swap_owner()
                            )
                    self.set_work_obj(obj)
                    obj.start()
                except Exception as e:
                    parse_except(e)
                sleep(nsec)
        except Exception as e:
            parse_except(e)
        finally:
            logger.critical(f"stop: {mod}")

    def work_b2vm(self, **kargs):
        try:
            logger.critical("start: b2vm")
            nsec = kargs.get("nsec", 0)
            mod = kargs.get("mod")
            assert mod is not None, f"mod name is None"
            dtype = self.get_dtype_from_mod(mod)
            while (self.__work_looping.get(mod, False)):
                logger.debug(f"looping: {mod}")
                try:
                    obj = b2vm.b2vm(mod,
                            dtype,
                            stmanage.get_btc_nodes(), 
                            stmanage.get_violas_nodes(),
                            stmanage.get_db(dtype), 
                            list(set(stmanage.get_receiver_address_list(dtype, "btc", False))),
                            list(set(stmanage.get_sender_address_list(dtype, "violas", False))),
                            stmanage.get_combine_address(dtype, "btc", True)
                            )
                    self.set_work_obj(obj)
                    obj.start()
                except Exception as e:
                    parse_except(e)
                sleep(nsec)
        except Exception as e:
            parse_except(e)
        finally:
            logger.critical(f"stop: {mod}")
    def work_v2b(self, **kargs):
        try:
            logger.critical("start: v2b")
            nsec = kargs.get("nsec", 0)
            mod = kargs.get("mod")
            assert mod is not None, f"mod name is None"
            dtype = self.get_dtype_from_mod(mod)
            while (self.__work_looping.get(mod, False)):
                logger.debug(f"looping: {mod}")
                try:
                    obj = v2b.v2b(mod, 
                            dtype,
                            stmanage.get_violas_nodes(), 
                            stmanage.get_btc_nodes(),
                            stmanage.get_db(dtype), 
                            list(set(stmanage.get_receiver_address_list(dtype, "violas", False))),
                            list(set(stmanage.get_sender_address_list(dtype, "btc", False))),
                            stmanage.get_combine_address(dtype, "violas"),
                            stmanage.get_swap_module(),
                            stmanage.get_swap_owner()
                            )
                    self.set_work_obj(obj)
                    obj.start()
                except Exception as e:
                    parse_except(e)
                sleep(nsec)
        except Exception as e:
            parse_except(e)
        finally:
            logger.critical(f"stop: {mod}")

    def work_v2bm(self, **kargs):
        try:
            logger.critical("start: v2bm")
            nsec = kargs.get("nsec", 0)
            mod = kargs.get("mod")
            assert mod is not None, f"mod name is None"
            dtype = self.get_dtype_from_mod(mod)
            while (self.__work_looping.get(mod, False)):
                logger.debug(f"looping: {mod}")
                try:
                    obj = v2bm.v2bm(mod, 
                            dtype,
                            stmanage.get_violas_nodes(), 
                            stmanage.get_btc_nodes(),
                            stmanage.get_db(dtype), 
                            list(set(stmanage.get_receiver_address_list(dtype, "violas", False))),
                            list(set(stmanage.get_sender_address_list(dtype, "btc", False))),
                            )
                    self.set_work_obj(obj)
                    obj.start()
                except Exception as e:
                    parse_except(e)
                sleep(nsec)
        except Exception as e:
            parse_except(e)
        finally:
            logger.critical(f"stop: {mod}")

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
            logger.critical(f"stop: {mod}")

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
                    ttype = "violas"
                    obj = analysis_proof.aproof(name=mod, ttype="violas", dtype=dtype, \
                            dbconf=stmanage.get_db(dtype), fdbconf=stmanage.get_db(basedata))
                    #set can receive token of violas transaction
                    if dtype == "v2bm":
                        obj.append_token_id(stmanage.get_support_map_token_id(ttype))
                    else:
                        obj.append_token_id(stmanage.get_support_stable_token_id(ttype))
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
            logger.critical(f"stop: {mod}")

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
            logger.critical(f"stop: {mod}")

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
                    ttype = "libra"
                    obj = analysis_proof.aproof(name=mod, ttype=ttype, dtype=dtype, \
                            dbconf=stmanage.get_db(dtype), fdbconf=stmanage.get_db(basedata))
                    #set can receive token of libra transaction
                    obj.append_token_id(stmanage.get_support_stable_token_id(ttype))
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
            logger.critical(f"stop: {mod}")

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
                    ttype = "violas"
                    obj = analysis_proof.aproof(name=mod, ttype=ttype, dtype=dtype, \
                            dbconf=stmanage.get_db(dtype), fdbconf=stmanage.get_db(basedata))
                    #set can receive token of violas transaction
                    if dtype == "v2lm":
                        obj.append_token_id(stmanage.get_support_map_token_id(ttype))
                    else:
                        obj.append_token_id(stmanage.get_support_stable_token_id(ttype))
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
            logger.critical(f"stop: {mod}")

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
                    obj = l2v.l2v(mod, 
                            dtype,
                            stmanage.get_violas_nodes(), 
                            stmanage.get_libra_nodes(),
                            stmanage.get_db(dtype), 
                            list(set(stmanage.get_receiver_address_list(dtype, "libra", False))),
                            list(set(stmanage.get_sender_address_list(dtype, "violas", False))),
                            stmanage.get_swap_module(),
                            stmanage.get_swap_owner(),
                            )
                    self.set_work_obj(obj)
                    obj.start()
                except Exception as e:
                    parse_except(e)
                sleep(nsec)
        except Exception as e:
            parse_except(e)
        finally:
            logger.critical(f"stop: {mod}")

    def work_l2vm(self, **kargs):
        try:
            logger.critical("start: l2vm")
            nsec = kargs.get("nsec", 0)
            mod = kargs.get("mod")
            assert mod is not None, f"mod name is None"

            #libra transaction's data types 
            dtype = self.get_dtype_from_mod(mod)
            while (self.__work_looping.get(mod, False)):
                logger.debug(f"looping: {mod}")
                try:
                    obj = l2vm.l2vm(mod, 
                            dtype,
                            stmanage.get_libra_nodes(),
                            stmanage.get_violas_nodes(), 
                            stmanage.get_db(dtype), 
                            list(set(stmanage.get_receiver_address_list(dtype, "libra", False))),
                            list(set(stmanage.get_sender_address_list(dtype, "violas", False)))
                            )
                    self.set_work_obj(obj)
                    obj.start()
                except Exception as e:
                    parse_except(e)
                sleep(nsec)
        except Exception as e:
            parse_except(e)
        finally:
            logger.critical(f"stop: {mod}")

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
                    obj = v2l.v2l(mod, 
                            dtype,
                            stmanage.get_violas_nodes(), 
                            stmanage.get_libra_nodes(),
                            stmanage.get_db(dtype), 
                            list(set(stmanage.get_receiver_address_list(dtype, "violas", False))),
                            list(set(stmanage.get_sender_address_list(dtype, "libra", False))),
                            stmanage.get_combine_address(dtype, "violas"),
                            stmanage.get_swap_module(),
                            stmanage.get_swap_owner(),
                            )
                    self.set_work_obj(obj)
                    obj.start()
                except Exception as e:
                    parse_except(e)
                sleep(nsec)
        except Exception as e:
            parse_except(e)
        finally:
            logger.critical(f"stop: {mod}")

    def work_v2lm(self, **kargs):
        try:
            logger.critical("start: v2lm")
            nsec = kargs.get("nsec", 0)
            mod = kargs.get("mod")
            assert mod is not None, f"mod name is None"

            #libra transaction's data types 
            dtype = self.get_dtype_from_mod(mod)
            while (self.__work_looping.get(mod, False)):
                logger.debug(f"looping: {mod}")
                try:
                    obj = v2lm.v2lm(mod, 
                            dtype,
                            stmanage.get_violas_nodes(), 
                            stmanage.get_libra_nodes(),
                            stmanage.get_db(dtype), 
                            list(set(stmanage.get_receiver_address_list(dtype, "violas", False))),
                            list(set(stmanage.get_sender_address_list(dtype, "libra", False))),
                            )
                    self.set_work_obj(obj)
                    obj.start()
                except Exception as e:
                    parse_except(e)
                sleep(nsec)
        except Exception as e:
            parse_except(e)
        finally:
            logger.critical(f"stop: {mod}")
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
            nsec = kargs.get("nsec", 0)
            mod = kargs.get("mod")
            assert mod is not None, f"mod name is None"
            logger.critical(f"start: btc {mod} proof")

            #libra transaction's data types 
            dtype = self.get_dtype_from_mod(mod)
            while (self.__work_looping.get(mod, False)):
                logger.debug(f"looping: {mod}")
                try:
                    basedata = "bfilter"
                    ttype = "btc"
                    obj = analysis_proof.aproof(name=mod, ttype=ttype, dtype=dtype, \
                            dbconf=stmanage.get_db(dtype), fdbconf=stmanage.get_db(basedata))
                    #set can receive token of btc transaction
                    obj.append_token_id(stmanage.get_support_stable_token_id(ttype))
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
            logger.critical(f"stop: {mod}")

    def work_b2lproof(self, **kargs):
        try:
            nsec = kargs.get("nsec", 0)
            mod = kargs.get("mod")
            assert mod is not None, f"mod name is None"
            logger.critical(f"start: btc {mod} proof")

            #libra transaction's data types 
            dtype = self.get_dtype_from_mod(mod)
            while (self.__work_looping.get(mod, False)):
                logger.debug(f"looping: {mod}")
                try:
                    basedata = "bfilter"
                    ttype = "btc"
                    obj = analysis_proof.aproof(name=mod, ttype=ttype, dtype=dtype, \
                            dbconf=stmanage.get_db(dtype), fdbconf=stmanage.get_db(basedata))
                    #set can receive token of btc transaction
                    obj.append_token_id(stmanage.get_support_stable_token_id(ttype))
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
            logger.critical(f"stop: {mod}")

    def work_b2l(self, **kargs):
        try:
            logger.critical("start: b2lxxx")
            nsec = kargs.get("nsec", 0)
            mod = kargs.get("mod")
            assert mod is not None, f"mod name is None"
            dtype = self.get_dtype_from_mod(mod)
            while (self.__work_looping.get(mod, False)):
                logger.debug(f"looping: {mod}")
                try:
                    obj = b2l.b2l(mod,
                            dtype,
                            stmanage.get_btc_nodes(), 
                            stmanage.get_violas_nodes(),
                            stmanage.get_libra_nodes(),
                            stmanage.get_db(dtype), 
                            list(set(stmanage.get_receiver_address_list(dtype, "btc", False))),
                            list(set(stmanage.get_sender_address_list(dtype, "libra", False))),
                            stmanage.get_combine_address(dtype, "violas", True),
                            stmanage.get_swap_module(),
                            stmanage.get_swap_owner()
                            )
                    self.set_work_obj(obj)
                    obj.start()
                except Exception as e:
                    parse_except(e)
                sleep(nsec)
        except Exception as e:
            parse_except(e)
        finally:
            logger.critical(f"stop: {mod}")

    def work_l2bproof(self, **kargs):
        try:
            nsec = kargs.get("nsec", 0)
            mod = kargs.get("mod")
            assert mod is not None, f"mod name is None"
            logger.critical(f"start: btc {mod} proof")

            #libra transaction's data types 
            dtype = self.get_dtype_from_mod(mod)
            while (self.__work_looping.get(mod, False)):
                logger.debug(f"looping: {mod}")
                try:
                    basedata = "lfilter"
                    ttype = "libra"
                    obj = analysis_proof.aproof(name=mod, ttype=ttype, dtype=dtype, \
                            dbconf=stmanage.get_db(dtype), fdbconf=stmanage.get_db(basedata))
                    #set can receive token of btc transaction
                    obj.append_token_id(stmanage.get_support_stable_token_id(ttype))
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
            logger.critical(f"stop: {mod}")

    def work_l2b(self, **kargs):
        try:
            logger.critical("start: l2b")
            nsec = kargs.get("nsec", 0)
            mod = kargs.get("mod")
            assert mod is not None, f"mod name is None"
            dtype = self.get_dtype_from_mod(mod)
            while (self.__work_looping.get(mod, False)):
                logger.debug(f"looping: {mod}")
                try:
                    obj = l2b.l2b(mod,
                            dtype,
                            stmanage.get_btc_nodes(), 
                            stmanage.get_violas_nodes(),
                            stmanage.get_libra_nodes(),
                            stmanage.get_db(dtype), 
                            list(set(stmanage.get_receiver_address_list(dtype, "libra", False))),
                            list(set(stmanage.get_sender_address_list(dtype, "btc", False))),
                            stmanage.get_combine_address(dtype, "violas", True),
                            stmanage.get_swap_module(),
                            stmanage.get_swap_owner()
                            )
                    self.set_work_obj(obj)
                    obj.start()
                except Exception as e:
                    parse_except(e)
                sleep(nsec)
        except Exception as e:
            parse_except(e)
        finally:
            logger.critical(f"stop: {mod}")

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
        def __init__(self, work, threadId, name, **kwargs):
            logger.debug(f"work thread __init__(work_funcs = {work.__name__} threadId = {threadId} name = {name}  kwargs = {kwargs})")
            threading.Thread.__init__(self)
            self.__threadId = threadId
            self.__name = name
            self.__kwargs = kwargs
            self.__work = work

        def run(self):
            logger.debug(f"work thread run{self.__kwargs}")
            self.__work(**self.__kwargs)

    def get_dtype_from_mod(self, modname):
        dtype = modname.lower()
        if dtype[:3] in ["v2b", "b2v", "l2v", "v2l", "b2l", "l2b"]:
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

    def is_match(self, name, startswith, endswith, fixlen):
        #print(f"name = {name}, startswith = {startswith} endswith = {endswith} fixlen = {fixlen}")
        lens = []
        if isinstance(fixlen, list):
            lens = fixlen
        elif isinstance(fixlen, int):
            lens.append(fixlen)
        else:
            raise Exception(f"fixlen type{type(fixlen)} is invalid.")
        return name.startswith(startswith) and len(name) in lens and name.endswith(endswith)

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
            elif self.is_match(name, "V2L", "PROOF", [11, 9]): #V2LXXXPROOF   V2LMPROOF
                self.funcs_map.update(self.create_func_dict(item, self.work_v2lproof))
            elif self.is_match(name, "V2B", "PROOF", [8, 9]):
                self.funcs_map.update(self.create_func_dict(item, self.work_v2bproof))
            elif self.is_match(name, "L2V", "PROOF", [11, 9]):
                self.funcs_map.update(self.create_func_dict(item, self.work_l2vproof))
            elif self.is_match(name, "L2B", "PROOF", 8):
                self.funcs_map.update(self.create_func_dict(item, self.work_l2bproof))
            elif self.is_match(name, "B2V", "PROOF", [11, 9]):
                self.funcs_map.update(self.create_func_dict(item, self.work_b2vproof))
            elif self.is_match(name, "B2L", "PROOF", 11):
                self.funcs_map.update(self.create_func_dict(item, self.work_b2lproof))
            elif self.is_match(name, "V2L", "EX", 8):
                self.funcs_map.update(self.create_func_dict(item, self.work_v2l))
            elif self.is_match(name, "V2B", "EX", 5):
                self.__funcs_map.update(self.create_func_dict(item, self.work_v2b))
            elif self.is_match(name, "L2V", "EX", 8): #L2VXXXEX
                self.funcs_map.update(self.create_func_dict(item, self.work_l2v))
            elif self.is_match(name, "L2B", "EX", 5):
                self.__funcs_map.update(self.create_func_dict(item, self.work_l2b))
            elif self.is_match(name, "B2V", "EX", 8):
                self.__funcs_map.update(self.create_func_dict(item, self.work_b2v))
            elif self.is_match(name, "B2L", "EX", 8):
                self.__funcs_map.update(self.create_func_dict(item, self.work_b2l))
            elif self.is_match(name, "V2LM", "EX", 6):
                self.funcs_map.update(self.create_func_dict(item, self.work_v2lm))
            elif self.is_match(name, "V2BM", "EX", 6):
                self.__funcs_map.update(self.create_func_dict(item, self.work_v2bm))
            elif self.is_match(name, "L2VM", "EX", 6): #L2VMEX
                self.funcs_map.update(self.create_func_dict(item, self.work_l2vm))
            elif self.is_match(name, "B2VM", "EX", 6):
                self.__funcs_map.update(self.create_func_dict(item, self.work_b2vm))
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
    #support_mods = stmanage.get_support_mods()
    for mod in work_mod:
    #    print(mod)
    #    if mod.endswith("EX"):
    #        dtype = mod[:-2]
    #    elif mod.endswith("PROOF"):
    #        dtype = mod[:-5]
    #    else:
    #        dtype = mod
    #    if dtype.lower() in support_mods:
    #        valid_mods.append(mod.name.lower())
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
        if mod == "all":
            for wm in work_mod:
                work_mods[wm.name.lower()] = True
            break
        else:
            work_mods[mod.lower()] = True

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
