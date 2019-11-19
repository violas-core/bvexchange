#!/usr/bin/python3
# coding default python2.x : ascii   python3.x :UTF-8
# -*- coding: UTF-8 -*-
import operator
import signal
import sys
import traceback
import log
import log.logger
import threading
from time import sleep, ctime
'''
'''
logger = log.logger.getLogger()



class works:
    __threads = []
    __work_b2v_looping = 1
    __work_v2b_looping = 1
    __work_comm_looping = 1
    def __init__(self):
        logger.debug("works __init__")
        self.__work_b2v_looping = 1
        self.__work_v2b_looping = 1
        self.__work_comm_looping = 1
        self.__threads = []

    def __del__(self):
        logger.debug("works __del__")
        del self.__threads

    def work_b2v(self, nsec):
        try:
            logger.debug("start: b2v")
            while (self.__work_b2v_looping):
                logger.debug("looping: b2v")
                sleep(nsec)
        except Exception as e:
            logger.error(traceback.format_exc(limit=1, file=sys.stdout))
        finally:
            logger.critical("stop: b2v")
    
    def work_v2b(self, nsec):
        try:
            logger.debug("start: v2b")
            while (self.__work_v2b_looping):
                logger.debug("looping: v2b")
                sleep(nsec)
        except Exception as e:
            logger.error(traceback.format_exc(limit=1, file=sys.stdout))
        finally:
            logger.critical("stop: v2b")
    
    def work_comm(self, nsec):
        try:
            logger.debug("start: comm")
            while(self.__work_comm_looping):
                logger.debug("looping: comm")
                sleep(nsec)
        except Exception as e:
            logger.error(traceback.format_exc(limit=1, file=sys.stdout))
        finally:
            logger.critical("stop: comm")
    
    class work_thread(threading.Thread):
        __name = ""
        __threadId = 0
        __type = ""
        __nsec = 1;
        __works = ""
        def __init__(self, works, threadId, name, type, nsec):
            logger.debug("work thread __init__: " + name)
            threading.Thread.__init__(self)
            self.__threadId = threadId
            self.__name = name
            self.__type = type
            self.__nsec = nsec
            self.__works = works
    
        def __del__(self):
            logger.debug("work thread __del__: %s", self.__name)
        def run(self):
            logger.debug("work thread run")
            if self.__type == "b2v":
                self.__works.work_b2v(self.__nsec)
            elif self.__type == "v2b":
                self.__works.work_v2b(self.__nsec)
            elif self.__type == "comm":
                self.__works.work_comm(self.__nsec)

    def start(self):
        try:
            logger.debug("start works")
    
            b2v = self.work_thread(self, 1, "b2v_thread", "b2v", 2)
            self.__threads.append(b2v)
    
            v2b = self.work_thread(self, 2, "v2b_thread", "v2b", 5)
            self.__threads.append(v2b)
    
            comm = self.work_thread(self, 3, "comm_thread", "comm", 7)
            self.__threads.append(comm)

            for work in self.__threads:
                work.start() #start work
        except Exception as e:
            logger.error(traceback.format_exc(limit=2, file=sys.stdout))
        finally:
            logger.critical("start end")

    def join(self):
        try:
            logger.debug("start join")
    
            for work in self.__threads:
                work.join() # work finish
        except Exception as e:
            logger.error(traceback.format_exc(limit=2, file=sys.stdout))
        finally:
            logger.critical("end join")
    
    def stop(self):
        logger.debug("stop works")
        self.__work_b2v_looping = 0
        self.__work_v2b_looping = 0
        self.__work_comm_looping = 0

work_manage = works()
def signal_stop(signal, frame):
    try:
        logger.debug("start signal : %i", signal )
        global work_manage
        work_manage.stop()
    except Exception as e:
        logger.error(traceback.format_exc(limit=2, file=sys.stdout))
    finally:
        logger.debug("end signal")

def main():
    try:
        logger.debug("start main")
        global work_manage
        signal.signal(signal.SIGINT, signal_stop)
        signal.signal(signal.SIGTSTP, signal_stop)
        work_manage.start()
        work_manage.join()
    except Exception as e:
        logger.error(traceback.format_exc(limit=2, file=sys.stdout))
    finally:
        logger.critical("main end")

if __name__ == '__main__':
    main()
