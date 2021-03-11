#!/usr/bin/python3
import operator
import sys
import json
import os
sys.path.append("..")
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../lbdiemsdk/src"))

import typing
import dataclasses
from dataclasses import (
        dataclass,
        asdict
        )

class field:
    def __init__(self, name, path = None, callback = None):
        self.name = name
        self.path = path if path else name
        self.callback = callback

    def parse(self, value):
        if self.callback:
            return self.callback(value)
        return value

class factory_base:

    PATH_SPLIT_SYMBOL = "."
    def __init__(self, account):
        self.__data = account
        self.__position = self.__data
        self.__init_show_fields_var()

    def __init_show_fields_var(self):
        self.__fields = []
        self.__default_output = {}

    def set_fields(self, fields):
        self.clear_fields()
        for field in fields: self.__fields.update({field.name : field})

    def append_fields(self, key, path, callback = None):
        self.__fields.update({key : self.field(key , path, callback)})

    def extend_fields(self, fields : typing.List[field]):
        for field in fields: self.__fields.update({field.name : field})

    def clear_fields(self):
        self.__fields = {}

    def append_default_output(self, key, value):
        self.__default_output.update({key:value})

    def extend_default_outputs(self, outputs):
        self.__default_output.update(outputs)

    def clear_default_outputs(self):
        self.__default_output = {}

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
        if name.startswith("__"):
            return self.__data

        if not self.__data:
            return {}
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

    def to_json(self):
        output = dict(self.__default_output)
        datas = {field.name: field.parse(self.get_attr_with_path(field.path)) for key, field in self.__fields.items()}
        output.update(datas)
        return output
        
    def get_field(self, name):
        return self.__fields.get(name)

    def get(name, default = None):
        field = self.get_field(name)
        return field if field else default

    @staticmethod
    def parse_list(datas):
        return [data for data in datas] if datas else []

