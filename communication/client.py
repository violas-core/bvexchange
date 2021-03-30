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
    def __init__(self, host, port = 8055, authkey = b"violas bridge communication", call = None, **kwargs):
        base.__init__(self, host, port, authkey)
        self.conn = Client(self.address, authkey = self.authkey)
        if call:
            self.start_connect(call, **kwargs)

    def __del__(self):
        if self.is_working():
            self.recv_thread.join()

    @property
    def connected(self):
        return self.conn and not self.conn.closed

    def work(self, call, **kwargs):
        while self.is_working() and self.connected:
            had_data = self.conn.poll(1)
            if had_data and self.connected:
                cmd = self.conn.recv()
                call(cmd, conn = self.conn)

    def start_connect(self, call, **kwargs):
        try:
            self.working = self.connected
            self.recv_thread = self.work_thread(self.work, call, **kwargs)
            self.recv_thread.start()
        except Exception as e:
            ret = parse_except(e)

    def send(self, cmd):
        if self.connected:
            self.conn.send(cmd)
        else:
            raise Exception(f"not connect to server(self.address)")

    def close(self):
        self.stop_work()
        if self.connected:
            self.conn.close()
