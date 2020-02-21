#!/usr/bin/python3
# coding default python2.x : ascii   python3.x :UTF-8
# -*- coding: UTF-8 -*-
'''
btc and vbtc exchange main
'''
import operator
import signal
import sys, os
#if len(sys.argv) > 1:
#    os.chdir(os.path.dirname(sys.argv[0]))
import traceback
import log
import log.logger
import threading
import stmanage
from time import sleep, ctime
import db
import db.dbb2v
import db.dbv2b
import comm.functions as fn
from exchange import b2v, v2b, exlv
from comm.result import parse_except
from analysis import analysis_base, analysis_filter, analysis_proof
import subprocess
from enum import Enum

name="bvexchange"

class work_mod(Enum):
    COMM    = 0
    B2V     = 1
    V2B     = 2
    VFILTER = 3
    V2BPROOF= 4
    LFILTER = 5
    L2VPROOF  = 6
    V2LPROOF= 7
    L2V     = 8
    V2L     = 9

class works:
    __threads = []
    __work_looping = {}
    __work_obj = {}

    __libra_min_valid_version   = 18323504
    __violas_min_valid_version  = 2000000
    def __init__(self):
        logger.debug("works __init__")
        for mod in self.__work_looping:
            self.__work_looping[mod.name] = 1

        self.__threads = []

    def __del__(self):
        del self.__threads

    def set_work_obj(self, obj):
        old_obj = self.__work_obj.get(obj.name())
        if old_obj is not None:
            del old_obj

        if obj.name() in self.__work_obj:
            del self.__work_obj[obj.name()]

        self.__work_obj[obj.name()] = obj

    def work_b2v(self, nsec):
        try:
            logger.critical("start: b2v")
            while (self.__work_looping.get(work_mod.B2V.name, False)):
                logger.debug("looping: b2v")
                try:
                    mod = "b2v"
                    chain = "violas"
                    obj = b2v.exb2v(mod,
                            stmanage.get_violas_nodes(), 
                            stmanage.get_btc_conn(), 
                            stmanage.get_module_address(mod, chain), 
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

    def work_v2b(self, nsec):
        try:
            logger.critical("start: v2b")
            while (self.__work_looping.get(work_mod.V2B.name, False)):
                logger.debug("looping: v2b")
                mod = "v2b"
                chain = "violas"
                try:
                    obj = v2b.exv2b(mod, 
                            stmanage.get_violas_nodes(), 
                            stmanage.get_btc_conn(), 
                            stmanage.get_db(mod), 
                            stmanage.get_module_address(mod, chain), 
                            list(set(stmanage.get_receiver_address_list(mod, chain))),
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

    def work_vfilter(self, nsec):
        try:
            logger.critical("start: violas filter")
            while (self.__work_looping.get(work_mod.VFILTER.name, False)):
                logger.debug("looping: vfilter")
                try:
                    dtype = "vfilter"
                    obj = analysis_filter.afilter(name="vfilter", ttype="violas", \
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

    def work_v2bproof(self, nsec):
        try:
            logger.critical("start: violas v2b proof")
            dtype = "v2b"   #violas transaction's data types 
            basedata = "vfilter"
            obj = analysis_proof.aproof(name="v2bproof", ttype="violas", dtype=dtype, \
                    dbconf=stmanage.get_db(dtype), fdbconf=stmanage.get_db(basedata))
            obj.set_step(stmanage.get_db(dtype).get("step", 100))
            obj.set_min_valid_version(self.__violas_min_valid_version - 1)
            self.set_work_obj(obj)
            while (self.__work_looping.get(work_mod.V2BPROOF.name, False)):
                logger.debug("looping: v2bproof")
                try:
                    obj.start()
                except Exception as e:
                    parse_except(e)
                sleep(nsec)
        except Exception as e:
            parse_except(e)
        finally:
            logger.critical("stop: v2bproof")

    def work_lfilter(self, nsec):
        try:
            logger.critical("start: libra filter")
            while (self.__work_looping.get(work_mod.LFILTER.name, False)):
                logger.debug("looping: lfilter")
                try:
                    dtype = "lfilter"
                    obj = analysis_filter.afilter(name="lfilter", ttype="libra", \
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

    def work_l2vproof(self, nsec):
        try:
            logger.critical("start: l2v proof")
            while (self.__work_looping.get(work_mod.L2VPROOF.name, False)):
                logger.debug("looping: l2vproof")
                try:
                    dtype = "l2v"   #libra transaction's data types 
                    basedata = "lfilter"
                    obj = analysis_proof.aproof(name="l2vproof", ttype="libra", dtype=dtype, \
                            dbconf=stmanage.get_db(dtype), fdbconf=stmanage.get_db(basedata))
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

    def work_v2lproof(self, nsec):
        try:
            logger.critical("start: violas v2l proof")
            dtype = "v2l"   #libra transaction's data types 
            basedata = "vfilter"
            obj = analysis_proof.aproof(name="v2lproof", ttype="violas", dtype=dtype, \
                    dbconf=stmanage.get_db(dtype), fdbconf=stmanage.get_db(basedata))
            obj.set_step(stmanage.get_db(dtype).get("step", 100))
            obj.set_min_valid_version(self.__violas_min_valid_version - 1)
            self.set_work_obj(obj)
            while (self.__work_looping.get(work_mod.V2LPROOF.name, False)):
                logger.debug("looping: v2lproof")
                try:
                    obj.start()
                except Exception as e:
                    parse_except(e)
                sleep(nsec)
        except Exception as e:
            parse_except(e)
        finally:
            logger.critical("stop: v2lproof")

    def work_l2v(self, nsec):
        try:
            logger.critical("start: l2v")
            while (self.__work_looping.get(work_mod.L2V.name, False)):
                logger.debug("looping: l2v")
                mod = "l2v"
                try:
                    obj = exlv.exlv(mod, 
                            stmanage.get_libra_nodes(),
                            stmanage.get_violas_nodes(), 
                            stmanage.get_db(mod), 
                            stmanage.get_module_address(mod, "libra"), 
                            stmanage.get_module_address(mod, "violas"), 
                            list(set(stmanage.get_receiver_address_list(mod, "libra"))),
                            list(set(stmanage.get_sender_address_list(mod, "violas"))),
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

    def work_v2l(self, nsec):
        try:
            logger.critical("start: v2l")
            while (self.__work_looping.get(work_mod.V2L.name, False)):
                logger.debug("looping: v2l")
                mod = "v2l"
                try:
                    obj = exlv.exlv(mod, 
                            stmanage.get_violas_nodes(), 
                            stmanage.get_libra_nodes(),
                            stmanage.get_db(mod), 
                            stmanage.get_module_address(mod, "violas"), 
                            stmanage.get_module_address(mod, "libra"), 
                            list(set(stmanage.get_receiver_address_list(mod, "violas"))),
                            list(set(stmanage.get_sender_address_list(mod, "libra"))),
                            "violas",
                            "libra")
                    self.set_work_obj(obj)
                    obj.start()
                except Exception as e:
                    parse_except(e)
                sleep(nsec)
        except Exception as e:
            parse_except(e)
        finally:
            logger.critical("stop: v2l")
    def work_comm(self, nsec):
        try:
            logger.critical("start: comm")
            while(self.__work_looping.get(work_mod.COMM.name, False)):
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
        def __init__(self, work, threadId, name, nsec):
            logger.debug("work thread __init__: name = %s  nsec = %i" ,name, nsec)
            threading.Thread.__init__(self)
            self.__threadId = threadId
            self.__name = name
            self.__nsec = nsec
            self.__work = work

        def run(self):
            logger.debug("work thread run")
            self.__work(self.__nsec)

    def thread_append(self, work, threadId, name, nsec):
        try:
            b2v = self.work_thread(work, threadId, name, nsec)
            self.__threads.append(b2v)
        except Exception as e:
            parse_except(e)
        finally:
            logger.debug("thread_append")

    def start(self, work_mods):
        try:
            logger.debug("start works")

            self.__work_looping = work_mods

            self.thread_append(self.work_comm, 0, "comm", stmanage.get_looping_sleep("comm"))

            if work_mods.get(work_mod.B2V.name, False):
                self.thread_append(self.work_b2v, work_mod.B2V.value, "b2v", stmanage.get_looping_sleep("b2v"))

            if work_mods.get(work_mod.V2B.name, False):
                self.thread_append(self.work_v2b, work_mod.V2B.value, "v2b", stmanage.get_looping_sleep("v2b"))

            if work_mods.get(work_mod.VFILTER.name, False):
                self.thread_append(self.work_vfilter, work_mod.VFILTER.value, "vfilter", stmanage.get_looping_sleep("vfilter"))

            if work_mods.get(work_mod.V2LPROOF.name, False):
                self.thread_append(self.work_v2lproof, work_mod.V2LPROOF.value, "v2lproof", stmanage.get_looping_sleep("v2lproof"))

            if work_mods.get(work_mod.V2BPROOF.name, False):
                self.thread_append(self.work_v2bproof, work_mod.V2BPROOF.value, "v2bproof", stmanage.get_looping_sleep("v2bproof"))

            if work_mods.get(work_mod.LFILTER.name, False):
                self.thread_append(self.work_lfilter, work_mod.LFILTER.value, "lfilter", stmanage.get_looping_sleep("lfilter"))

            if work_mods.get(work_mod.L2VPROOF.name, False):
                self.thread_append(self.work_l2vproof, work_mod.L2VPROOF.value, "l2vproof", stmanage.get_looping_sleep("l2vproof"))

            if work_mods.get(work_mod.L2V.name, False):
                self.thread_append(self.work_l2v, work_mod.L2V.value, "l2v", stmanage.get_looping_sleep("l2v"))

            if work_mods.get(work_mod.V2L.name, False):
                self.thread_append(self.work_v2l, work_mod.V2L.value, "v2l", stmanage.get_looping_sleep("v2l"))

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

def run(mods):
    valid_mods = ["all"]
    for mod in work_mod:
        valid_mods.append(mod.name.lower())

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
        work_mods[mod.upper()] = True
        if mod == "all":
            for wm in work_mod:
                work_mods[wm.name.upper()] = True
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
