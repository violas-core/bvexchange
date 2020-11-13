#!/usr/bin/python3
import operator
import sys, getopt
import json
sys.path.append("..")
import traceback
import datetime
#from .models import BtcRpc
from enum import Enum

#module name
name="parseargs"

class parseargs:
    __args = {}
    __args_priority = {}
    __args_argtype = {}
    __unique = []

    class argtype(Enum):
        LIST = 0x01
        STR  = 0x02
        JSON = 0x03

    def __init__(self):
        pass

    def __del__(self):
        pass

    def appendunique(self, opts_unique):
        if opts_unique is None:
            return
        self.__unique.append(list(opts_unique))

    def check_unique(self, opts):
        opt_list = [name.replace("--", "") for name in opts]
        for uni in self.__unique:
            count = 0
            for opt in opt_list:
                if opt in uni:
                    count += 1
                if count > 1:
                    print(f"found Mutually exclusive parameters ({uni})")
                    sys.exit(2)


    def isvalid(self, name):
        arg = name[2:]
        return arg in [key.replace('-', '') for key in self.__args.keys()]

    def hasarg(self, name):
        for arg in self.__args.keys():
            if arg.find('-') >= 0 and name[2:] == arg.replace('-', ''):
                return True
        return False

    def append(self, name, desc, hasarg = False, arglist = None, priority = 100, argtype = argtype.LIST):
        if name in self.__args:
            raise Exception("arg is exists.")
        if hasarg:
            key = f"{name}-"
            value = f"desc: {desc} format: --{name} \"{arglist}\""
        else:
            key = name
            value = f"desc: {desc} format: --{name}"
        self.__args[key] = value
        self.__args_priority[name] = priority
        self.__args_argtype[name] = argtype

    def remove(self, name):
        if self.__args is None or name not in self.__args:
            return
        del self.__args[name]
        del self.__args_priority[name]

    def show_args(self):
        for key in list(self.__args.keys()):
            print("{}{} \n\t\t\t\t{}".format("--", key.replace('-', ''), self.__args[key].replace('\n', '')))
        sys.exit(2)

    def exit_error_opt(self, opt):
        print(self.__args["{}-".format(opt.replace('--', ''))])
        sys.exit(2)

    def __show_arg_info(self, info):
        print(info)


    def list_arg_name(self):
        return [ "--" + arg.replace('-', "") for arg in self.args.keys()]

    def show_help(self, args):
        if args is not None and len(args) > 0 and args[0] == "--help":
            self.show_args()

        if args is None or len(args) == 0:
            self.show_args()

        if args is None or len(args) != 2 or args[0] != "help" :
            find = False
            for name in args:
                if find == True:
                    find = False
                    continue
                if self.isvalid(name) == False:
                    self.show_args()
                if self.hasarg(name) == True:
                    find = True
            return

        name = args[1]

        if name in self.__args:
            self.__show_arg_info("--{} \n\t{}".format(name, self.__args[name].replace("format:", "\n\tformat:")))
        else:
            self.__show_arg_info("--{} \n\t{}".format(name, self.__args["{}-".format(name)].replace("format:", "\n\tformat:")))

        sys.exit(2)

    def __sort_opts(self, opts):
        sorted_opts = []
        for opt in opts:
            for i, sopt in enumerate(sorted_opts):
                if self.__args_priority[opt[0][2:]] < self.__args_priority[sopt[0][2:]]:
                    sorted_opts.insert(i, opt)
                    break
            else:
                sorted_opts.append(opt)
        return sorted_opts

    def getopt(self, argv):
        opts, err_msg = getopt.getopt(argv, None, [arg.replace('-', "=") for arg in self.__args.keys()])
        opts = self.__sort_opts(opts)
        return (opts, err_msg)

    def is_matched(self, opt, names):
        nl = [ "--" + name for name in names]
        return opt in nl

    def split_arg(self, opt, arg):
        if arg is None:
            return (0, None)

        #arg is not json format
        if self.__args_argtype[opt.replace("-", "")] == self.argtype.STR:
            arg_list = [arg]
        elif self.__args_argtype[opt.replace("-", "")] == self.argtype.STR:
            arg_list = json.loads(argstr)
        else:
            if "," not in arg:
                argstr = "[\"{}\"]".format(arg)
            else:
                argstr = "[{}]".format(arg)
            arg_list = json.loads(argstr)
        return  (len(arg_list), arg_list)

    def exit_check_opt_arg(self, opt, arg, arg_count):
        count, arg_list = self.split_arg(opt, arg)
        counts = []
        if isinstance(arg_count, int):
            counts.append(arg_count)
        if count not in counts:
            self.exit_error_opt(opt)

    def exit_check_opt_arg_min(self, opt, arg, arg_count):
        count, arg_list = self.split_arg(opt, arg)
        if count < arg_count:
            self.exit_error_opt(opt)
