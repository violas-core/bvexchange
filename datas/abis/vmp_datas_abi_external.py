import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../"))
from datas.abis.metafiles import metainfos

BYTECODE    =   ""
(ABI, ADDRESS) = metainfos.load_abi_address("datas", "external")

