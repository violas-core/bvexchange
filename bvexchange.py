#!/usr/bin/python3
# coding default python2.x : ascii   python3.x :UTF-8
# -*- coding: UTF-8 -*-
'''
btc and vbtc exchange main
'''
import operator
import signal
import sys, os
if len(sys.argv) > 0:
    os.chdir(os.path.dirname(sys.argv[0]))
sys.path.append("./packages")
sys.path.append("./packages/libra-client")
import traceback
import log
import log.logger
import threading
import setting
from time import sleep, ctime
import db
import db.dbb2v
import db.dbv2b
from exchange import b2v, v2b
from comm.result import parse_except
from violasanalysis import violas_filter
import subprocess
from enum import Enum

name="bvexchange"

def checkrerun():
    proc = subprocess.Popen(["pgrep", "-f", __file__], stdout=subprocess.PIPE)
    std = proc.communicate()
    if len(std[0].decode().split()) > 1:
        exit("already running")
    proc = subprocess.Popen(["pgrep", "-f", "bvmanage.py"], stdout=subprocess.PIPE)
    std = proc.communicate()
    if len(std[0].decode().split()) > 1:
        exit("already running")

class work_mod(Enum):
    ALL = 0
    B2V = 1
    V2B = 2
    VFILTER = 3

class works:
    __threads = []
    __work_b2v_looping = 1
    __work_v2b_looping = 1
    __work_vf_looping = 1
    __work_comm_looping = 1
    __mod = work_mod.ALL


    def __init__(self):
        logger.debug("works __init__")
        self.__work_b2v_looping = 1
        self.__work_v2b_looping = 1
        self.__work_comm_looping = 1
        self.__work_vf_looping = 1
        self.__threads = []

    def __del__(self):
        del self.__threads

    def work_b2v(self, nsec):
        try:
            logger.debug("start: b2v")
            while (self.__work_b2v_looping):
                logger.debug("looping: b2v")
                b2v.works()
                sleep(nsec)
        except Exception as e:
            parse_except(e)
        finally:
            logger.critical("stop: b2v")
    
    def work_v2b(self, nsec):
        try:
            logger.debug("start: v2b")
            while (self.__work_v2b_looping):
                logger.debug("looping: v2b")
                v2b.works()
                sleep(nsec)
        except Exception as e:
            parse_except(e)
        finally:
            logger.critical("stop: v2b")
    
    def work_vfilter(self, nsec):
        try:
            logger.debug("start: violas filter")
            while (self.__work_vf_looping):
                logger.debug("looping: vfilter")
                violas_filter.works()
                sleep(nsec)
        except Exception as e:
            parse_except(e)
        finally:
            logger.critical("stop: vfilter")
    def work_comm(self, nsec):
        try:
            logger.debug("start: comm")
            while(self.__work_comm_looping):
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

    def start(self, mod = work_mod.ALL):
        try:
            logger.debug("start works")
    
            if mod == work_mod.ALL or mod == work_mod.B2V:
                self.thread_append(self.work_b2v, 1, "b2v", setting.b2v_sleep)

            if mod == work_mod.ALL or mod == work_mod.V2B:
                self.thread_append(self.work_v2b, 2, "v2b", setting.v2b_sleep)

            if mod == work_mod.ALL or mod == work_mod.VFILTER:
                self.thread_append(self.work_vfilter, 3, "vfilter", setting.vfilter_sleep)

            self.thread_append(self.work_comm, 4, "comm", setting.comm_sleep)
            
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
        self.__work_b2v_looping = 0
        self.__work_v2b_looping = 0
        self.__work_vf_looping = 0
        self.__work_comm_looping = 0


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

def write_pid():
    try:
        f = open("bvexchange.pid", mode='w')
        f.write(f"{os.getpid()}")
        f.close()
    except Exception as e:
        parse_except(e)


def run(mod):
    
    print(mod)
    if mod is None or mod not in ["all", "b2v", "v2b", "vfilter"]:
        raise Exception("mod is invalid [all, b2v, v2b, vfilter].")

    checkrerun()
    write_pid()
    global work_manage
    logger.debug("start main")
    
    signal.signal(signal.SIGINT, signal_stop)
    signal.signal(signal.SIGTSTP, signal_stop)
    signal.signal(signal.SIGTERM, signal_stop)
    work_manage.start(work_mod[mod.upper()])
    work_manage.join()

def main(argc, argv):
    try:
        if argc != 1:
             raise Exception(f"argument is invalid")
        run(argv[0])
    except Exception as e:
        parse_except(e)
    finally:
        logger.critical("main end")

if __name__ == '__main__':
    main(len(sys.argv) - 1, sys.argv[1:])
