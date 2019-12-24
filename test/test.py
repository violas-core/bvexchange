#!/usr/bin/python3
# coding default python2.x : ascii   python3.x :UTF-8
# -*- coding: UTF-8 -*-
import operator
import signal
import sys, os
print(os.getcwd())
sys.path.append("..")
import traceback
import log
import log.logger
import threading
import hashlib 
import binascii
from time import sleep, ctime
'''
'''
logger = log.logger.getLogger("test")
class MyNumbers:
    def __iter__(self):
        self.b = 1
        return self
    
    def __next__(self):
        if self.b <= 10:
            x = self.b
            self.b += 1
            return x
        else:
            raise StopIteration

class testclass:
    _name = "testclass"

def hello():
    hwe = "hello, \
            world"
    Hwe = "Hello, world"
    hwc = ""

    print(Hwe)

    port = 102

    print("port = %d", port)
    if hwe:
        print(hwe)
        print(hwc)
        print(hwe)

def test_list():
    a = 1
    b = 2
    c = 3

    if not (a and b or c):
        print("not a and b or c ")

    al = [1, 2, 4, 5]
    if (a in al):
        print(a)

    if (c in al):
        print(c)

    d = 0
    if (d not in al): 
        print(d)

    list_1 = ["string", 1, 1.0, "string end"]
    print(list_1)

    list_1.append("append string")
    print(list_1)
    print("print index = -2")
    print(list_1[-2])
    print("print index = -3")
    print(list_1[-3])

    print("after deleting value at index 2")
    del list_1[2]
    print(list_1)

    list_cmp1 = [1,2,3]
    list_cmp2 = [5,6,7]
    list_cmp3 = [5,6,7]
    print(operator.eq(list_cmp1, list_cmp2))
    print(operator.eq(list_cmp3, list_cmp2))
    print(len(list_cmp1))
    print(max(list_cmp1))

def test():
    myclass = MyNumbers()
    myiter = iter(myclass)

    print("my iter")
    for x in myiter:
        print(x)

def test_dict():
    dict = {"name" : "dict", "age" : 10}
    print("dict[name]" , dict["name"])
    print("dict[age]" , dict["age"])

def main():
    print("main")

def func1():
    raise Exception("-- func1 exception --")

def test_except():
    try:
        func1()
    except Exception as e:
        exc_type, exc_value, exc_traceback_obj = sys.exc_info()
        logger.error("exc_type : ", exc_type)
        logger.error("exc_value : ", exc_value)
        logger.error("exc_traceback_obj : ", exc_traceback_obj)
        #traceback.print_tb(exc_traceback_obj)
        #traceback.print_exception(exc_type, exc_value, exc_traceback_obj, limit=3, file=sys.stdout)
        logger.error(traceback.format_exc(limit=1, file=sys.stdout))
def parse(e):
    try:
        raise e
    except IOError as e:
        logger.debug("ioerror")
    except ZeroDivisionError as e:
        logger.debug("ZeroDivisionError")
    except Exception as e:
        logger.debug("Exception")
def test_except_parse():
    try:
        f = open("a", 'r')
    except Exception as e:
        parse(e)
def test_logging():
    logger.debug('This is a customer debug message')
    logger.info('This is an customer info message')
    logger.warning('This is a customer warning message')
    logger.error('This is an customer error message')
    logger.critical('This is a customer critical message')

def test_hash():
    hashlib.pbkdf2_hmac("sha3-256","adsf".encode('utf-8'), b"test", 1024)
    #print(hashlib.sha3_256("qqqqqqqqqqqqqqqqqqqqqqqq".encode('utf-8')).hexdigest())

if __name__ == "__main__":
    test_hash()
