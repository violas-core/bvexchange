#!/usr/bin/python3

import sys

name="values"

COINS = 1000000  # map to satoshi/100
MIN_EST_GAS = 1000 * COINS / 100000000  #estimate min gas value(satoshi), check wallet address's balance is enough 

EX_TYPE_B2V = "b2v"
EX_TYPE_V2B = "v2b"

VIOLAS_ADDRESS_LEN = [32, 64]
