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
    def __init__(self):
        logger.debug("works __init__")
        self.work_b2v_looping = 1
        self.work_v2b_looping = 1
        self.work_comm_looping = 1
        self.threads = []

    def work_b2v(self, nsec):
        try:
            logger.debug("start: b2v")
            while (self.work_b2v_looping):
                logger.debug("looping: b2v")
                sleep(nsec)
        except Exception as e:
            logger.error(traceback.format_exc(limit=1, file=sys.stdout))
        finally:
            logger.critical("stop: b2v")
    
    def work_v2b(self, nsec):
        try:
            logger.debug("start: v2b")
            while (self.work_b2v_looping):
                logger.debug("looping: v2b")
                sleep(nsec)
        except Exception as e:
            logger.error(traceback.format_exc(limit=1, file=sys.stdout))
        finally:
            logger.critical("stop: v2b")
    
    def work_comm(self, nsec):
        try:
            logger.debug("start: comm")
            while(self.work_comm_looping):
                logger.debug("looping: comm")
                sleep(nsec)
        except Exception as e:
            logger.error(traceback.format_exc(limit=1, file=sys.stdout))
        finally:
            logger.critical("stop: comm")
    
    class work_thread(threading.Thread):
        def __init__(self, works, threadid, name, type, nsec):
            logger.debug("work thread __init__:", name)
            threading.Thread.__init__(self)
            self.threadId = threadid
            self.name = name
            self.type = type
            self.nsec = nsec
            self.works = works
    
        def run(self):
            logger.debug("work thread run")
            if self.type == "b2v":
                self.works.work_b2v(self.nsec)
            elif self.type == "v2b":
                self.works.work_v2b(self.nsec)
            elif self.type == "comm":
                self.works.work_comm(self.nsec)

    def start(self):
        try:
            logger.debug("start works")
    
            b2v = self.work_thread(self, 1, "b2v_thread", "b2v", 2)
            self.threads.append(b2v)
    
            v2b = self.work_thread(self, 2, "v2b_thread", "v2b", 5)
            self.threads.append(v2b)
    
            comm = self.work_thread(self, 3, "comm_thread", "comm", 7)
            self.threads.append(comm)

            for work in self.threads:
                work.start() #start work
        except Exception as e:
            logger.error(traceback.format_exc(limit=2, file=sys.stdout))
        finally:
            logger.critical("start end")

    def join(self):
        try:
            logger.debug("start join")
    
            for work in self.threads:
                self.work.join() # work finish
        except Exception as e:
            logger.error(traceback.format_exc(limit=2, file=sys.stdout))
        finally:
            logger.critical("end join")
    
    def stop(self):
        logger.debug("stop works")
        self.work_b2v_looping = 0
        self.work_v2b_looping = 0
        self.work_comm_looping = 0

work_manage = works()
def signal_stop(signal, frame):
    logger.debug("start signal")
    global work_manage
    work_manage.stop()

def main():
    try:
        logger.debug("start main")
        global work_manage
        signal.signal(signal.SIGINT, signal_stop)
        work_manage.start()
    except Exception as e:
        logger.error(traceback.format_exc(limit=2, file=sys.stdout))
    finally:
        logger.critical("main end")

if __name__ == '__main__':
    main()
