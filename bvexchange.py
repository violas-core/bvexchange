#!/usr/bin/python3
# coding default python2.x : ascii   python3.x :UTF-8
# -*- coding: UTF-8 -*-
'''
btc and vbtc exchange main
'''
import operator
import signal
import sys
sys.path.append("./packages")
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
import subprocess

name="bvexchange"

def checkrerun():
    proc = subprocess.Popen(["pgrep", "-f", __file__], stdout=subprocess.PIPE)
    std = proc.communicate()
    if len(std[0].decode().split()) > 1:
        exit("already running")

class works:
    __threads = []
    __work_b2v_looping = 1
    __work_v2b_looping = 1
    __work_comm_looping = 1
    __traceback_limit = 0
    def __init__(self, traceback_limit):
        logger.debug("works __init__")
        self.__work_b2v_looping = 1
        self.__work_v2b_looping = 1
        self.__work_comm_looping = 1
        self.__threads = []
        self.__traceback_limit = traceback_limit

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
            logger.error(traceback.format_exc(limit=self.__traceback_limit))
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
            logger.error(traceback.format_exc(limit=self.__traceback_limit))
        finally:
            logger.critical("stop: v2b")
    
    def work_comm(self, nsec):
        try:
            logger.debug("start: comm")
            while(self.__work_comm_looping):
                logger.debug("looping: comm")
                sleep(nsec)
        except Exception as e:
            logger.error(traceback.format_exc(limit=self.__traceback_limit))
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
            logger.error(traceback.format_exc(limit=self.__traceback_limit))
        finally:
            logger.debug("thread_append")

    def start(self):
        try:
            logger.debug("start works")
    
            #self.thread_append(self.work_b2v, 1, "b2v", setting.b2v_sleep)
            self.thread_append(self.work_v2b, 2, "v2b", setting.v2b_sleep)
            #self.thread_append(self.work_comm, 3, "comm", setting.comm_sleep)
            
            for work in self.__threads:
                work.start() #start work

        except Exception as e:
            logger.error(traceback.format_exc(limit=self.__traceback_limit))
        finally:
            logger.critical("start end")

    def join(self):
        try:
            logger.debug("start join")
    
            for work in self.__threads:
                work.join() # work finish
        except Exception as e:
            logger.error(traceback.format_exc(limit=self.__traceback_limit))
        finally:
            logger.critical("end join")
    
    def stop(self):
        logger.debug("stop works")
        self.__work_b2v_looping = 0
        self.__work_v2b_looping = 0
        self.__work_comm_looping = 0


logger = log.logger.getLogger(name)
work_manage = works(setting.traceback_limit)
def signal_stop(signal, frame):
    try:
        logger.debug("start signal : %i", signal )
        global work_manage
        work_manage.stop()
    except Exception as e:
        logger.error(traceback.format_exc(limit=setting.traceback_limit))
    finally:
        logger.debug("end signal")

def main():
    try:
        global work_manage
        logger.debug("start main")
        signal.signal(signal.SIGINT, signal_stop)
        signal.signal(signal.SIGTSTP, signal_stop)
        work_manage.start()
        work_manage.join()
    except Exception as e:
        logger.error(traceback.format_exc(limit=setting.traceback_limit))
    finally:
        logger.critical("main end")

if __name__ == '__main__':
    checkrerun()
    main()
