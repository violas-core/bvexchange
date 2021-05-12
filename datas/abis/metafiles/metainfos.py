import json
import sys
import os
import typing

abi_files = {
        "main" : "ViolasMProofMain.abi",
        "datas": "ViolasMProofDatas.abi",
        "state": "ViolasMProofState.abi"
        }
contract_conf_files = {
        "internal" : "vlscontract_internal.json",
        "external" : "vlscontract_external.json",
        }

MOUDLE  = typing.Literal["main", "datas", "state"]
CHAIN   = typing.Literal["internal", "external"]

FIX_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)))

def get_abspath(filename):
    return os.path.join(FIX_PATH, filename);

def load_abi_address(module : MOUDLE, chain_type : CHAIN):
    conf_file = get_abspath(contract_conf_files[chain_type])
    abis_file = get_abspath(abi_files[module]);

    if not os.path.exists(conf_file):
        raise FileExistsError(f"{conf_file} not found.")

    if not os.path.exists(abis_file):
        raise FileExistsError(f"{abis_file} not found.")

    abi_data = ""
    with open(abis_file, "r") as fs:
        abi_data = fs.read();
    
    with open(conf_file, "r") as fs:
        confs   = json.load(fs)
        address = confs[module]["address"]

    return (abi_data, address)
