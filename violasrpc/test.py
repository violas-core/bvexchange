#!/usr/bin/python3

import json, decimal
import requests
from authproxy import AuthServiceProxy, JSONRPCException


#libra
#url = 'http://client.testnet.libra.org'

#violas external
url = 'http://ac.testnet.violas.io:50001'

#violas internal 
#url = 'http://52.27.228.84:50001'

class FancyFloat(float):
    def __repr__(self):
        return format(Decimal(self), "f")

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
           return float(o)
         
        super().default(o)

def json_print(data):
    if data is None:
        print("")
    print(json.dumps(data, sort_keys=True, cls= DecimalEncoder, indent=5))

def json_dumps(data):
    if data is None:
        print("")
    return json.dumps(data, sort_keys=True, cls= DecimalEncoder, indent=5)

def json_reset(data):
    if data is None:
        return {}
    return json.loads((json.dumps(data, sort_keys=True, cls= DecimalEncoder, indent=5)))


def main():
    ui = AuthServiceProxy(url)
    ret = ui.get_transactions(23709089, 1, True)
    json_print(ret)

    #ret = ui.get_currencies()
    #json_print(ret)

if __name__ == "__main__":
    main()
