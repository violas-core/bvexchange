# CONTENT

**Note**: The Mapping token and receiver address and may be updated in the future.

## Overview

support chain: ethereum btc violas
bitcoin : testnet
ethereum chainid 42
violas: internal chain

## Version

v1.0.1

## Tokens
* BTC : bitcoin token
* VBTC : violas token of BTC
* Vsdt : ethereum erc20 token (USDT)
* VUSDT : violas token of usdt

## Mapping type
* BTC -> VBTC
* VBTC -> BTC
* usdt -> VUSDT
* VUSDT -> usdt

## receiver or contract address list

 name     | address | type | chain | desc 
 :---     | :---:   | :---: | :---:  | :---
 ustd     | 0xb64DB0d1810De2548534c003e2E5503564D7f3E5 | contract | kovan(ethereum) | call approve
 proof    | 0x045B0Dc3908B0c00001E35871250cA3D598E3F32 | contract | kovan(ethereum) | call transferProof
 map-ERC20| 00000000000000000042524755534454           | DD       | violas          | receiver address of mapping: map-coin -> ethereum erc20 token
 map-BTC  | 0000000000000000004252472d425443           | DD       | violas          | receiver address of mapping: VBTC -> BTC 
 map-VBTC | 2MxBZG7295wfsXaUj69quf8vucFzwG35UWh        | address  | bitcoin         | receiver address of mapping: BTC -> VBTC
 funds    | 00000000000000000042524746554e44           | DD       | violas          | funds manager
 
