#! /usr/bin/pydoc3
from comm.result import (
        parse_except,
        )
from multiprocessing.connection import (
        Client,
        Listener,
        wait,
        )

from array import array
from communication.base import (
        base,
        )

import comm.error
import comm.result
import comm.values


name = "multi_server"

class server(base):
    def __init__(self, host, port = 8055, authkey = b"violas bridge communication"):
        base.__init__(self, host, port, authkey)
        self.__listen_thread = None
        self.listener = Listener(self.address, authkey = self.authkey)

    def __del__(self):
        self.listen_thread.join()
        print("close server")
        pass

    def listen(self, call, **kwargs):
        try:
            self.working = self.listener is not None
            while self.is_working():
                with self.listener.accept() as conn:
                      print('connection accepted from', self.listener.last_accepted)
                      while self.is_working():
                          try:
                            cmd = conn.recv()
                            call(cmd, conn = conn, listener = self.listener)
                          except Exception as e:
                              print(f"connect error: {e}")
                              break
        except Exception as e:
            parse_except(e)


    
    def start_listen(self, call, **kwargs):
        try:
            self.listen_thread = self.work_thread(self.listen, call, **kwargs)
            
            self.listen_thread.start()
        except Exception as e:
            ret = parse_except(e)

    def stop(self):
        self.working = False
        if self.listener:
            self.listener.close()


