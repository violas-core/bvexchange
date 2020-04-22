#!/usr/bin/python3
# coding default python2.x : ascii   python3.x :UTF-8
# -*- coding: UTF-8 -*-
'''
btc and vbtc exchange main
'''
import operator
import signal
import sys, os
import log
import json
import log.logger
import threading
import subprocess
import fcntl
import comm.values
from comm.result import result, parse_except

VIOLAS_ADDRESS_LEN = comm.values.VIOLAS_ADDRESS_LEN

def checkrerun(rfile):
    print(f"*************************{rfile}")
    proc = subprocess.Popen(["pgrep", "-f", rfile], stdout=subprocess.PIPE)
    std = proc.communicate()
    if len(std[0].decode().split()) > 1:
        exit("already running")

def write_pid(name):
    try:
        f = open(f"{name}.pid", mode='w')
        f.write(f"{os.getpid()}\n")
        f.close()
    except Exception as e:
        parse_except(e)

def pid_name(name):
    return f"{name}.pid"

class filelock:
    def __init__(self, name):
        self.fobj = open(pid_name(name), 'w')
        self.fd = self.fobj.fileno()

    def __del__(self):
        self.unlock()
    def lock(self):
        try:
            fcntl.lockf(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except Exception as e:
            return False

    def unlock(self):
        try:
            self.fobj.close()
        except Exception as e:
            pass

def json_print(data):
    print(json.dumps(data, sort_keys=True, indent=4))

def split_full_address(address, auth_key_prefix = None):
    try:
        new_address = address
        if address is not None and isinstance(address, bytes):
            new_address = address.hex()

        new_auth_key_prefix = None
        if new_address is not None and len(new_address) == max(VIOLAS_ADDRESS_LEN):
            new_address = new_address[32:]
            new_auth_key_prefix = new_address[:32]

        if auth_key_prefix is not None:
            if isinstance(auth_key_prefix, bytes):
                new_auth_key_prefix = auth_key_prefix.hex()
            else:
                new_auth_key_prefix = auth_key_prefix

        if new_auth_key_prefix == "00000000000000000000000000000000":
            new_auth_key_prefix = None

        return (new_auth_key_prefix, new_address) 
    except Exception as e:
        pass
    return None

def merge_full_address(address, auth_key_prefix = None):
    try:
        new_address = address
        if address is not None and isinstance(address, bytes):
            new_address = address.hex()

        new_auth_key_prefix = None
        if auth_key_prefix is not None:
            if isinstance(auth_key_prefix, bytes):
                new_auth_key_prefix = auth_key_prefix.hex()
            else:
                new_auth_key_prefix = auth_key_prefix
            new_address = f"f{new_auth_key_prefix}{address}"
        if new_address is not None and len(new_address) < max(VIOLAS_ADDRESS_LEN):
            new_address = f"{00000000000000000000000000000000}{new_address}"

        return new_address 
    except Exception as e:
        pass
    return None
