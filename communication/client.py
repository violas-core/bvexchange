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


name = "multi_client"

class client(base):
    def __init__(self, host, port = 8055, authkey = b"violas bridge communication"):
        base.__init__(self, host, port, authkey)

    def __del__(self):
        self.recv_thread.join()
        print("close client")
        pass

    def connect(self, call, **kwargs):
        while self.is_working():
            cmd = self.conn.recv()
            call(cmd, conn = self.conn)

    def start_connect(self, call, **kwargs):
        try:
            self.conn = Client(self.address, authkey = self.authkey)
            self.working = self.conn is not None
            self.recv_thread = self.work_thread(self.connect, call, **kwargs)
            self.recv_thread.start()
        except Exception as e:
            ret = parse_except(e)

    def send(self, cmd):
        if self.conn:
            self.conn.send(cmd)

    def close(self):
        base.close(self)
        self.conn.close()

