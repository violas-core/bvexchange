import json
import os
import sys
sys.path.append("../")

from datas.abis.metafiles import metainfos

BYTECODE    =   ""
(ABI, ADDRESS) = metainfos.load_abi_address("datas", "internal")

