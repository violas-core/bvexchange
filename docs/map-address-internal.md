# CONTENT

**Note**: The Mapping token and receiver address and may be updated in the future.

## Overview

support chain: ethereum btc violas
bitcoin : testnet
ethereum chainid: 42(kovan)
violas: internal chain

## Version

v1.0.1

## Tokens
* BTC : bitcoin token
* vBTC : violas token of BTC
* usdt : ethereum erc20 token (USDT)
* vUSDT : violas token of usdt

## Support mapping type
* BTC -> vBTC
* vBTC -> BTC
* usdt -> vUSDT
* vUSDT -> usdt

## receiver or contract address list

 name     | address | type | chain | desc 
 :---     | :---:   | :---: | :---:  | :---
 ustd     | 0x6f08730dA8e7de49a4064d2217c6B68d7E61E727 | contract | kovan(ethereum) | call approve
 proof    | 0xC600601D8F3C3598628ad996Fe0da6C8CF832C02 | contract | kovan(ethereum) | call transferProof
 map-ERC20| 00000000000000000042524755534454           | DD       | violas          | receiver address of mapping: map-coin -> ethereum erc20 token
 map-BTC  | 0000000000000000004252472d425443           | DD       | violas          | receiver address of mapping: vBTC -> BTC 
 map-vBTC | 2N2YasTUdLbXsafHHmyoKUYcRRicRPgUyNB        | address  | bitcoin         | receiver address of mapping: BTC -> vBTC
 funds    | 00000000000000000042524746554e44           | DD       | violas          | funds manager
 


