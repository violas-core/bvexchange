#! /usr/bin/pydoc3
import threading
from comm.result import (
        parse_except,
        )

from comm.exception_ext import (
        ReadonlyException,
        )


class base(object):
    def __init__(self, host, port = 8055, authkey = b"violas bridge communication"):
        self.host = host
        self.port = port
        self.address = (self.host, self.port)
        self.authkey = authkey
        self.working = False
        print(f"start communication host = {self.host} port = {self.port} authkey = {self.authkey}")
        

    def __del__(self):
        print("close")

    class work_thread(threading.Thread):
        def __init__(self, call, parse_msg, **kwargs):
            print(f"work thread __init__(kwargs = {kwargs})")
            threading.Thread.__init__(self)
            self.__kwargs = kwargs
            self.__call = call
            self.__parse_msg = parse_msg

        def run(self):
            self.__call(self.__parse_msg, **self.__kwargs)

    @property
    def can_read_write(self):
        return ("working", "listener", "conn", "call")

    
    def can_write(self, name):
        if name not in self.__dict__ or name in self.can_read_write:
            return True
        return False

    def __setattr__(self, name, value):
        if not self.can_write(name):
            raise ReadonlyException(name)
        else:
            object.__setattr__(self, name, value)

    def rmproperty(self, name):
        if name in self.__dict__:
            del self.__dict__[name]

    def is_working(self):
        return self.working

    def stop_work(self):
        print("base.stop_work")
        self.working = False

    def call(self, cmd, conn = None, listener = None, **kwargs):
        pass


