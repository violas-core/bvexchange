#!/usr/bin/python3
import operator
import sys
import json
import os
sys.path.append("..")
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../lbdiemsdk/src"))

class factory_base:
    PATH_SPLIT_SYMBOL = "."
    def __init__(self, account):
        self.__data = account
        self.__position = self.__data

    def reset(func):
        def reset_pos_decorate(*args, **kwargs):
            self = args[0]
            args = list(args[1:])
            self.reset_pos()
            return func(self, *args, **kwargs)
        return reset_pos_decorate

    def reset_pos(self):
        self.__position = self.__data

    def __getattr__(self, name):
        return getattr(self.__data, name)

    def __repr__(self):
        return self.__data.__repr__()

    def get_attr_with_path(self, path):
        fields = path.split(self.PATH_SPLIT_SYMBOL)
        parent = self.__data
        for field in fields:
            data = getattr(parent, field)
            if not data:
                return None

            parent = data
        return data



