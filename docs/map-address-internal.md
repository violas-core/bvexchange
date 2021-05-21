# CONTENT

**Note**: The Mapping token and receiver address and may be updated in the future.

## Overview

support chain:  ethereum btc violas
bitcoin :       testnet
ethereum chainid: 42(kovan)
violas:         internal chain

## Version

v1.0.1

## Tokens
* BTC :         bitcoin token
* VBTC :        violas token of BTC
* [tokenname]:  ethereum erc20 token (USDT)
* VUSDT :       violas token of usdt

## Support mapping type
* BTC   -> VBTC
* VBTC  -> BTC
* erc20 -> VERC20
### erc20 list
[erc20 tokens](https://github.com/palliums-developers/violas-sol/blob/work/jsons/tokens/erc20_tokens_internal.md)

## receiver or contract address list

 name     | address | type | chain | desc 
 :---     | :---:   | :---: | :---:  | :---
 ustd     | 0x6f08730dA8e7de49a4064d2217c6B68d7E61E727 | contract | kovan(ethereum) | call approve
 proof    | 0xc6aC75b3B3f6E48Ac1228a34C2732d1F0b9BF934 | contract | kovan(ethereum) | call transferProof
 map-ERC20| 00000000000000000042524755534454           | DD       | violas          | receiver address of mapping: map-coin -> ethereum erc20 token
 map-BTC  | 0000000000000000004252472d425443           | DD       | violas          | receiver address of mapping: VBTC -> BTC 
 map-VBTC | 2N2YasTUdLbXsafHHmyoKUYcRRicRPgUyNB        | address  | bitcoin         | receiver address of mapping: BTC -> VBTC
 funds    | 00000000000000000042524746554e44           | DD       | violas          | funds manager
 

