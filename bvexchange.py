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
sys.path.append("./packages")
sys.path.append("./packages/libra-client")
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
from exchange import b2v, v2b
from comm.result import parse_except
from analysis import violas_base, violas_filter, violas_proof
import subprocess
from enum import Enum


name="bvexchange"

class work_mod(Enum):
    COMM    = 0
    B2V     = 1
    V2B     = 2
    VFILTER = 3
    VPROOF  = 4

class works:
    __threads = []
    __work_looping = {}
    __v2b = None
    __b2v = None
    __vfilter = None
    __vproof = None
    __lproof = None
    __l2v = None
    __v2l = None
    

    def __init__(self):
        logger.debug("works __init__")
        for mod in self.__work_looping:
            self.__work_looping[mod.name] = 1
            
        self.__threads = []

    def __del__(self):
        del self.__threads

    def work_b2v(self, nsec):
        try:
            logger.debug("start: b2v")
            while (self.__work_looping.get(work_mod.B2V.name, False)):
                logger.debug("looping: b2v")
                self.__b2v = b2v.exb2v()
                self.__b2v.work()
                sleep(nsec)
        except Exception as e:
            parse_except(e)
        finally:
            logger.critical("stop: b2v")
    
    def work_v2b(self, nsec):
        try:
            logger.debug("start: v2b")
            while (self.__work_looping.get(work_mod.V2B.name, False)):
                logger.debug("looping: v2b")
                self.__v2b = b2v.exb2v()
                self.__v2b.work()
                sleep(nsec)
        except Exception as e:
            parse_except(e)
        finally:
            logger.critical("stop: v2b")
    
    def work_vfilter(self, nsec):
        try:
            logger.debug("start: violas filter")
            while (self.__work_looping.get(work_mod.VFILTER.name, False)):
                logger.debug("looping: vfilter")
                dtype = "vfilter"
                self.__vfilter = violas_filter.vfilter(name="vfilter", ttype="violas", \
                        dbconf=stmanage.get_db(dtype), vnodes=stmanage.get_violas_nodes())
                self.__vfilter.set_step(stmanage.get_db(dtype).get("step", 1000))
                self.__vfilter.work()
                sleep(nsec)
        except Exception as e:
            parse_except(e)
        finally:
            logger.critical("stop: vfilter")

    def work_vproof(self, nsec):
        try:
            logger.debug("start: violas proof")
            while (self.__work_looping.get(work_mod.VPROOF.name, False)):
                logger.debug("looping: vproof")
                dtype = "v2b"
                basedata = "vfilter"
                self.__vproof = violas_proof.vproof(name="v2bproof", ttype="violas", dtype=dtype, \
                        dbconf=stmanage.get_db(dtype), vfdbconf=stmanage.get_db(basedata), vnodes=stmanage.get_violas_nodes())
                self.__vproof.set_step(stmanage.get_db(dtype).get("step", 100))
                self.__vproof.work()
                sleep(nsec)
        except Exception as e:
            parse_except(e)
        finally:
            logger.critical("stop: vproof")

    def work_comm(self, nsec):
        try:
            logger.debug("start: comm")
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

            if work_mods.get(work_mod.B2V.name, False):
                self.thread_append(self.work_b2v, 1, "b2v", stmanage.get_looping_sleep("b2v"))

            if work_mods.get(work_mod.V2B.name, False):
                self.thread_append(self.work_v2b, 2, "v2b", stmanage.get_looping_sleep("v2b"))

            if work_mods.get(work_mod.VFILTER.name, False):
                self.thread_append(self.work_vfilter, 3, "vfilter", stmanage.get_looping_sleep("vfilter"))

            if work_mods.get(work_mod.VPROOF.name, False):
                self.thread_append(self.work_vproof, 4, "vproof", stmanage.get_looping_sleep("vproof"))

            self.thread_append(self.work_comm, 5, "comm", stmanage.get_looping_sleep("comm"))
            
            for work in self.__threads:
                work.start() #start work

        except Exception as e:
            parse_except(e)
        finally:
            logger.critical("start end")

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
    for mod in mods:
        if mod is None or mod not in ["all", "b2v", "v2b", "vfilter", "vproof"]:
            raise Exception(f"mod({mod}) is invalid [all, b2v, v2b, vfilter, vproof].")

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

    print(f"work_mods= {work_mods}")
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
