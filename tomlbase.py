#!/usr/bin/python3
import os, sys
#import setting
from comm import result
from comm.result import parse_except
from comm.functions import (
        json_print, 
        root_path
        )
from comm.parseargs import parseargs
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "tomlkit"))

from tomlkit.toml_document import TOMLDocument
from tomlkit.toml_file import TOMLFile
from pathlib import Path
from comm.values import (
        PROJECT_NAME
        )


class tomlbase():
    def __init__(self, tomlfile = None):
        self.__toml = None
        self.__content = None
        self._toml_file = ""
        self.__load_conf()
        self.__dataproof = {}

    def __load_conf(self):

        self.__dataproof = {}
        filename = self.__get_conf_file()
        if filename is None or not self.get_conf_env():
            self.is_loaded = False
            return 

        self._toml_file = filename 
        self.__toml = TOMLFile(filename)
        self.__content = self.toml.read()
        self.__dataproof.update({"conf_file":filename})

        assert isinstance(self.__content, TOMLDocument)
        self.is_loaded = True
        for key, value in self.__content.items():
            setattr(self, key, value)
            self.__dataproof.update({key:value})

    def __get_conf_file(self):
        release_path = ""
        toml_file = self.get_conf_env()
        if toml_file is None or not os.path.exists(toml_file):
            return toml_file

        path = Path(toml_file)
        if not path.is_file() or not path.exists():
            raise Exception(f"not found toml file: {toml_file}")
        return toml_file

    
    @property
    def is_loaded(self):
        return self.__is_loaded

    @is_loaded.setter
    def is_loaded(self, value):
        self.__is_loaded = value

    def __check_load_conf(self):
        if not self.is_loaded:
            self.__load_conf()

    def reset(self):
        self.__load_conf()
        if not self.is_loaded:
            toml_file = self.get_conf_env()
            raise Exception(f"not found toml file: {toml_file}")

    @property
    def datas(self):
        return self.__dataproof

    @property
    def toml_file(self):
        return self._toml_file

    @property
    def toml(self):
        return self.__toml

    @property
    def content(self):
        self.__check_load_conf()
        if not self.is_loaded:
            print("not found configure file(toml). use --conf ")
            sys.exit(-1)
        return self.__content

    def keys(self):
        return self.__dataproof.keys()

    def set(self, key, value):
        return self.__dataproof.update({key:value})

    def get(self, key, default = None):
        self.__check_load_conf()
        if not self.is_loaded:
            print("not found configure file(toml). use --conf ")
            sys.exit(-1)
        return self.__dataproof.get(key, default)

    @classmethod
    def set_conf_env(self, conffile):
        os.environ["BVEXCHANGE_CONFIG"] = conffile

    @classmethod
    def get_conf_env(self):
        return os.environ.get("BVEXCHANGE_CONFIG", None)

    @classmethod
    def set_conf_env_default(self):
        basename = PROJECT_NAME
        print(basename)
        os.environ["BVEXCHANGE_CONFIG"] = os.path.join(f"/etc/{basename}/", f"{basename}.toml")

def main():
    tomlbase.set_conf_env_default()
    print(tomlbase.get_conf_env())
    pass



if __name__ == "__main__":
    main()
