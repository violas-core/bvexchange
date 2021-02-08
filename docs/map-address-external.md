# CONTENT

**Note**: The Mapping token and receiver address and may be updated in the future.

## Overview

support chain: ethereum btc violas
bitcoin : testnet
ethereum chainid 42
violas: internal chain

## Version

v1.0.0

## Tokens

BTC : bitcoin token
vBTC : violas token of BTC
usdt : ethereum erc20 token (USDT)
vUSDT : violas token of usdt

## Mapping type
   BTC -> vBTC
   vBTC -> BTC
   usdt -> vUSDT
   vUSDT -> usdt

## receiver or contract address list

### address : 0xb64DB0d1810De2548534c003e2E5503564D7f3E5
    type : ethereum contract address
    desc : usdt contract address of kovan(chainid = 42) usdt approve

### address : 0x045B0Dc3908B0c00001E35871250cA3D598E3F32
    type : ethereum contract address
    desc : call transferProof and token manage, usdt -> vUSDT

### address : 00000000000000000042524755534454
    type: violas address(DD account)
    desc : receiver address for vUSDT -> usdt

### address : 0000000000000000004252472d425443
    type: violas address(DD account)
    desc : receiver address for vBTC -> BTC

### address : 2MxBZG7295wfsXaUj69quf8vucFzwG35UWh
    type : bitcoin address (testnet)
    desc : receiver address BTC -> vBTC

### address : 00000000000000000042524746554e44
    type: violas address(DD account)
    desc : funds manage

