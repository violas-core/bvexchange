# CONTENT

**Note**: The Mapping Protocol Specification is under development and may be updated in the future.

## Overview

Mapping Protocol is based on the [OP_RETURN](https://github.com/bitcoin/bitcoin/blob/master/doc/release-notes/release-notes-0.12.0.md#relay-any-sequence-of-pushdatas-in-op_return-outputs-now-allowed) formats.This Specification defines the mapping types, and provides usage examples.

## Version

v1.3.0




---




## OP_RETURN - format

OP_RETURN compact_size mark datas

### Attributes

<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong>OP_RETURN</strong></td>
  <td>byte</td>
  <td>op code type</td>
 </tr>
 <tr>
  <td><strong>compact_size</strong></td>
  <td>uint8/(uint8 + uint8)</td>
  <td>Compressed number, sizeof(compact_size) + sizeof(mark) + sizeof(datas)</td>
 </tr>
 <tr>
  <td><strong>mark</strong></td>
  <td>bytes(6)</td>
  <td>mark for violas</td>
 </tr>
 <tr>
  <td><strong>datas</strong></td>
  <td>bytes</td>
  <td>mapping datas</td>
 </tr>

</table>


## Fix-value 


### Attributes

<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Value</strong></td>
 </tr>
 <tr>
  <td><strong>OP_RETURN</strong></td>
  <td>byte</td>
  <td>0x6a</td>
 </tr>
 <tr>
  <td><strong>mark</strong></td>
  <td>bytes(6)</td>
  <td>0x76696f6c6173</td>
 </tr>

</table>

## compact_size

size = len(mark) + len(datas)

### Attributes

<table>
 <tr>
  <td><strong>Type</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Condition</strong></td>
 </tr>
 <tr>
  <td><strong>uint8<strong></td>
  <td>size</td>
  <td>size < 76</td>
 </tr>
 <tr>
  <td><strong>uint16</strong></td>
  <td>uint8: 0x4c + uint8:size</td>
  <td>size >= 76</td>
 </tr>
</table>


## Fields - type

**Description**

[payload](#Payloads) use fields


### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Stored Format</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Versions---type">version</a></strong></td>
  <td>uint16</td>
  <td>big-endian</td>
  <td>Mapping protocol version</td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>uint16</td>
  <td>big-endian</td>
  <td>transaction type</td>
 </tr>
 <tr>
  <td><strong>payee_address</strong></td>
  <td>char(16)</td>
  <td>address:16</td>
 </tr>
 <tr>
  <td><strong>sequence</strong></td>
  <td>uint64</td>
  <td>big-endian</td>
  <td>transaction sequence. ex: timestamps </td>
 </tr>
 <tr>
  <td><strong>module_address</strong></td>
  <td>char(16)</td>
  <td>address:16</td>
 </tr>
 <tr>
  <td><strong>violas_amount</strong></td>
  <td>uint64</td>
  <td>big-endian</td>
  <td>transaction microamount(1000000).</td>
 </tr>
 <tr>
  <td><strong>btc_amount</strong></td>
  <td>uint64</td>
  <td>big-endian</td>
  <td>transaction satoshi(100000000).</td>
 </tr>
 <tr>
  <td><strong>violas_version</strong></td>
  <td>uint64</td>
  <td>big-endian</td>
  <td>violas transaction version</td>
 </tr>
 <tr>
  <td><strong>out_amount</strong></td>
  <td>uint64</td>
  <td>big-endian</td>
  <td>swap out put token amount(min out amount) microamount(1000000).</td>
 </tr>
 <tr>
  <td><strong>times</strong></td>
  <td>uint16</td>
  <td>big-endian</td>
  <td>retry times if swap failed. 
      times = 0 : always swap until swap succeed  
      times > 0: refund token to payer when retry number of times is max 
  </td>
 </tr>
</table>


## Versions - type

**Description**

transaction version code


### Attributes


<table>
 <tr>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong>0x0001</strong></td>
  <td>start version</td>
 </tr>
 <tr>
  <td><strong>0x0002</strong></td>
  <td>violas chain version is v0.9.0 or up</td>
 </tr>
 <tr>
  <td><strong>0x0003</strong></td>
  <td>violas chain version is v0.18.0 or up</td>
 </tr>
</table>


## Types - type

**Description**

transaction type code


### Attributes


<table>
 <tr>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong>0x1030</strong></td>
  <td><strong>btc Deposit certificate</strong></td>
 </tr>
 <tr>
  <td><strong>0x3000</strong></td>
  <td>request mapping violas token btc</td>
 </tr>
 <tr>
  <td><strong>0x3001</strong></td>
  <td>mapping violas token completed</td>
 </tr>
 <tr>
  <td><strong>0x3002</strong></td>
  <td>mapping violas token cancel. (no-use)</td>
 </tr>
 <tr>
  <td><strong>0x3010</strong></td>
  <td>violas token mapping btc mark</td>
 </tr>
 <tr>
  <td><strong>0x4000</strong></td>
  <td>btc swap violas vlsusd token</td>
 </tr>
 <tr>
  <td><strong>0x4001</strong></td>
  <td>btc swap violas vlseur token</td>
 </tr>
 <tr>
  <td><strong>0x4002</strong></td>
  <td>btc swap violas vlssgd token</td>
 </tr>
 <tr>
  <td><strong>0x4003</strong></td>
  <td>btc swap violas vlsgbp token</td>
 </tr>
 <tr>
  <td><strong>0x5000</strong></td>
  <td>btc swap libra usd token</td>
 </tr>
 <tr>
  <td><strong>0x5001</strong></td>
  <td>btc swap libra eur token</td>
 </tr>
 <tr>
  <td><strong>0x5002</strong></td>
  <td>btc swap libra sgd token</td>
 </tr>
 <tr>
  <td><strong>0x5003</strong></td>
  <td>btc swap libra gbp token</td>
 </tr>
</table>




---




## Payloads 

**Description**

btc transaction's OP_RETURN datas



### mapping violas btc - start

**Description**

btc mapping violas token(btc) request


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Versions---type">version</a></strong></td>
  <td>0x0003</td>
  <td></td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>0x3000</td>
  <td></td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">payee_address</a></strong></td>
  <td>c91806cabcd5b2b5fa25ae1c50bed3c6</td>
  <td>payee address</td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">sequence</a></strong></td>
  <td>20200110006</td>
  <td>timestamps</td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">module_address</a></strong></td>
  <td>524689a4f870c46d6a5d901b5ac1fdb2</td>
  <td>module address of violas swap(btc)</td>
 </tr>
</table>

```
hex-Vstr: 6a3276696f6c617300033000c91806cabcd5b2b5fa25ae1c50bed3c600000004b40537b6524689a4f870c46d6a5d901b5ac1fdb2

fields:
    OP_RETURN head:
        6a : OP_RETURN(0x6a)
        32 : data len(50)
    payload datas:
        76696f6c6173 : mark(violas)
        0003 : version(0x0003)
        3000 : type(0x3000)
        c91806cabcd5b2b5fa25ae1c50bed3c6 : payee_address
        00000004b40537b6 : sequence(20200110006)
        524689a4f870c46d6a5d901b5ac1fdb2 : module_address
```


### mapping - end

**Description**

btc mapping violas token end


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Versions---type">version</a></strong></td>
  <td>0x0003</td>
  <td></td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>0x3001</td>
  <td></td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">payee_address</a></strong></td>
  <td>c91806cabcd5b2b5fa25ae1c50bed3c6</td>
  <td>payee address</td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">sequence</a></strong></td>
  <td>20200110006</td>
  <td>timestamps</td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">violas_amount</a></strong></td>
  <td>10000</td>
  <td>micro amount. scaling factor:1000000</td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">violas_version</a></strong></td>
  <td>1000</td>
  <td>Mapping vtoken transaction version</td>
 </tr>
</table>

```
hex-Vstr: 6a3276696f6c617300033001c91806cabcd5b2b5fa25ae1c50bed3c600000004b40537b60000000000002710000000000000271A

fields:
    OP_RETURN head:
        6a : OP_RETURN(0x6a)
        32 : data len(50)
    payload datas:
        76696f6c6173 : mark(violas)
        0003 : version(0x0003)
        3001 : type(0x3001)
        c91806cabcd5b2b5fa25ae1c50bed3c6 : payee_address
        00000004b40537b6 : sequence(20200110006)
        000000000002710 : violas_amount(10000)
        00000000000271A : violas_version(10010)
``` 

### deposit_certificate

**Description**

btc transaction Deposit certificate


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Versions---type">version</a></strong></td>
  <td>0x0003</td>
  <td></td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>0x1030</td>
  <td></td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">payee_address</a></strong></td>
  <td>c91806cabcd5b2b5fa25ae1c50bed3c6</td>
  <td>payee address</td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">sequence</a></strong></td>
  <td>20200110006</td>
  <td>timestamps</td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">btc_amount</a></strong></td>
  <td>10000</td>
  <td>satoshi. scaling factor:100000000</td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">mark_name</a></strong></td>
  <td>violas</td>
  <td>mark name, unique in chain</td>
 </tr>
</table>

```
hex-Vstr: 6a3176696f6c617300031030c91806cabcd5b2b5fa25ae1c50bed3c600000004b40537b6000000000000271076696f6c617300

fields:
    OP_RETURN head:
        6a : OP_RETURN(0x6a)
        31 : data len(49)
    payload datas:
        76696f6c6173 : mark(violas)
        0003 : version(0x0003)
        1030 : type(0x1030)
        c91806cabcd5b2b5fa25ae1c50bed3c6 : payee_address
        00000004b40537b6 : sequence(20200110006)
        0000000000002710 : btc_amount(10000)
        76696f6c617300 : mark_name(violas + '\0')
``` 

### swap violas vlsusd - start

**Description**

btc swap violas token(vlsusd) request


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Versions---type">version</a></strong></td>
  <td>0x0003</td>
  <td></td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>0x4000</td>
  <td></td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">payee_address</a></strong></td>
  <td>c91806cabcd5b2b5fa25ae1c50bed3c6</td>
  <td>payee address</td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">sequence</a></strong></td>
  <td>20200110006</td>
  <td>timestamps</td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">module_address</a></strong></td>
  <td>524689a4f870c46d6a5d901b5ac1fdb2</td>
  <td>module address of violas swap(btc)</td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">out_amount</a></strong></td>
  <td>1000000</td>
  <td>swap violas btc token amount microamount(1000000) </td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">times</a></strong></td>
  <td>0</td>
  <td>retry swap violas btc token number of times</td>
 </tr>
</table>

```
hex-Vstr: 6a3c76696f6c617300034000c91806cabcd5b2b5fa25ae1c50bed3c600000004b40537b6524689a4f870c46d6a5d901b5ac1fdb200000000000027100000

fields:
    OP_RETURN head:
        6a : OP_RETURN(0x6a)
        3c : data len(60)
    payload datas:
        76696f6c6173 : mark(violas)
        0003 : version(0x0003)
        4000 : type(0x4000)
        c91806cabcd5b2b5fa25ae1c50bed3c6 : payee_address
        00000004b40537b6 : sequence(20200110006)
        524689a4f870c46d6a5d901b5ac1fdb2 : module_address
        0000000000002710 : out_amount(10000)
        0000 : times(0)
```

### swap violas vlseur - start

**Description**

btc swap violas token(vlseur) request


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Versions---type">version</a></strong></td>
  <td>0x0003</td>
  <td></td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>0x4001</td>
  <td></td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">payee_address</a></strong></td>
  <td>c91806cabcd5b2b5fa25ae1c50bed3c6</td>
  <td>payee address</td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">sequence</a></strong></td>
  <td>20200110006</td>
  <td>timestamps</td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">module_address</a></strong></td>
  <td>524689a4f870c46d6a5d901b5ac1fdb2</td>
  <td>module address of violas swap(btc)</td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">out_amount</a></strong></td>
  <td>1000000</td>
  <td>swap violas btc token amount microamount(1000000) </td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">times</a></strong></td>
  <td>0</td>
  <td>retry swap violas btc token number of times</td>
 </tr>
</table>

```
hex-Vstr: 6a3c76696f6c617300034001c91806cabcd5b2b5fa25ae1c50bed3c600000004b40537b6524689a4f870c46d6a5d901b5ac1fdb200000000000027100000

fields:
    OP_RETURN head:
        6a : OP_RETURN(0x6a)
        3c : data len(60)
    payload datas:
        76696f6c6173 : mark(violas)
        0003 : version(0x0003)
        4001 : type(0x4001)
        c91806cabcd5b2b5fa25ae1c50bed3c6 : payee_address
        00000004b40537b6 : sequence(20200110006)
        524689a4f870c46d6a5d901b5ac1fdb2 : module_address
        0000000000002710 : out_amount(10000)
        0000 : times(0)
```

### swap violas vlssgd - start

**Description**

btc swap violas token(vlssgd) request


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Versions---type">version</a></strong></td>
  <td>0x0003</td>
  <td></td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>0x4002</td>
  <td></td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">payee_address</a></strong></td>
  <td>c91806cabcd5b2b5fa25ae1c50bed3c6</td>
  <td>payee address</td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">sequence</a></strong></td>
  <td>20200110006</td>
  <td>timestamps</td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">module_address</a></strong></td>
  <td>524689a4f870c46d6a5d901b5ac1fdb2</td>
  <td>module address of violas swap(btc)</td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">out_amount</a></strong></td>
  <td>1000000</td>
  <td>swap violas btc token amount microamount(1000000) </td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">times</a></strong></td>
  <td>0</td>
  <td>retry swap violas btc token number of times</td>
 </tr>
</table>

```
hex-Vstr: 6a3c76696f6c617300034002c91806cabcd5b2b5fa25ae1c50bed3c600000004b40537b6524689a4f870c46d6a5d901b5ac1fdb200000000000027100000

fields:
    OP_RETURN head:
        6a : OP_RETURN(0x6a)
        3c : data len(60)
    payload datas:
        76696f6c6173 : mark(violas)
        0003 : version(0x0003)
        4002 : type(0x4002)
        c91806cabcd5b2b5fa25ae1c50bed3c6 : payee_address
        00000004b40537b6 : sequence(20200110006)
        524689a4f870c46d6a5d901b5ac1fdb2 : module_address
        0000000000002710 : out_amount(10000)
        0000 : times(0)
```

### swap violas vlsgbp - start

**Description**

btc swap violas token(vlsgbp) request


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Versions---type">version</a></strong></td>
  <td>0x0003</td>
  <td></td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>0x4003</td>
  <td></td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">payee_address</a></strong></td>
  <td>c91806cabcd5b2b5fa25ae1c50bed3c6</td>
  <td>payee address</td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">sequence</a></strong></td>
  <td>20200110006</td>
  <td>timestamps</td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">module_address</a></strong></td>
  <td>524689a4f870c46d6a5d901b5ac1fdb2</td>
  <td>module address of violas swap(btc)</td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">out_amount</a></strong></td>
  <td>1000000</td>
  <td>swap violas btc token amount microamount(1000000) </td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">times</a></strong></td>
  <td>0</td>
  <td>retry swap violas btc token number of times</td>
 </tr>
</table>

```
hex-Vstr: 6a3c76696f6c617300034003c91806cabcd5b2b5fa25ae1c50bed3c600000004b40537b6524689a4f870c46d6a5d901b5ac1fdb200000000000027100000

fields:
    OP_RETURN head:
        6a : OP_RETURN(0x6a)
        3c : data len(60)
    payload datas:
        76696f6c6173 : mark(violas)
        0003 : version(0x0003)
        4003 : type(0x4003)
        c91806cabcd5b2b5fa25ae1c50bed3c6 : payee_address
        00000004b40537b6 : sequence(20200110006)
        524689a4f870c46d6a5d901b5ac1fdb2 : module_address
        0000000000002710 : out_amount(10000)
        0000:times(0)
```

### swap libra usd - start

**Description**

btc swap libra token(usd) request


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Versions---type">version</a></strong></td>
  <td>0x0003</td>
  <td></td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>0x5000</td>
  <td></td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">payee_address</a></strong></td>
  <td>c91806cabcd5b2b5fa25ae1c50bed3c6</td>
  <td>payee address</td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">sequence</a></strong></td>
  <td>20200110006</td>
  <td>timestamps</td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">module_address</a></strong></td>
  <td>524689a4f870c46d6a5d901b5ac1fdb2</td>
  <td>module address of violas swap(btc)</td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">out_amount</a></strong></td>
  <td>1000000</td>
  <td>swap violas btc token amount microamount(1000000) </td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">times</a></strong></td>
  <td>0</td>
  <td>retry swap violas btc token number of times</td>
 </tr>
</table>

```
hex-Vstr: 6a3c76696f6c617300035000c91806cabcd5b2b5fa25ae1c50bed3c600000004b40537b6524689a4f870c46d6a5d901b5ac1fdb200000000000027100000

fields:
    OP_RETURN head:
        6a : OP_RETURN(0x6a)
        3c : data len(60)
    payload datas:
        76696f6c6173 : mark(violas)
        0003 : version(0x0003)
        5000 : type(0x5000)
        c91806cabcd5b2b5fa25ae1c50bed3c6 : payee_address
        00000004b40537b6 : sequence(20200110006)
        524689a4f870c46d6a5d901b5ac1fdb2 : module_address
        0000000000002710 : out_amount(10000)
        0000:times(0)
```

### swap libra eur - start

**Description**

btc swap libra token(eur) request


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Versions---type">version</a></strong></td>
  <td>0x0003</td>
  <td></td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>0x5001</td>
  <td></td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">payee_address</a></strong></td>
  <td>c91806cabcd5b2b5fa25ae1c50bed3c6</td>
  <td>payee address</td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">sequence</a></strong></td>
  <td>20200110006</td>
  <td>timestamps</td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">module_address</a></strong></td>
  <td>524689a4f870c46d6a5d901b5ac1fdb2</td>
  <td>module address of violas swap(btc)</td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">out_amount</a></strong></td>
  <td>1000000</td>
  <td>swap violas btc token amount microamount(1000000) </td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">times</a></strong></td>
  <td>0</td>
  <td>retry swap violas btc token number of times</td>
 </tr>
</table>

```
hex-Vstr: 6a3c76696f6c617300034001c91806cabcd5b2b5fa25ae1c50bed3c600000004b40537b6524689a4f870c46d6a5d901b5ac1fdb200000000000027100000

fields:
    OP_RETURN head:
        6a : OP_RETURN(0x6a)
        3c : data len(60)
    payload datas:
        76696f6c6173 : mark(violas)
        0003 : version(0x0003)
        5001 : type(0x5001)
        c91806cabcd5b2b5fa25ae1c50bed3c6 : payee_address
        00000004b40537b6 : sequence(20200110006)
        524689a4f870c46d6a5d901b5ac1fdb2 : module_address
        0000000000002710 : out_amount(10000)
        0000:times(0)
```

### swap libra sgd - start

**Description**

btc swap libra token(sgd) request


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Versions---type">version</a></strong></td>
  <td>0x0003</td>
  <td></td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>0x5002</td>
  <td></td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">payee_address</a></strong></td>
  <td>c91806cabcd5b2b5fa25ae1c50bed3c6</td>
  <td>payee address</td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">sequence</a></strong></td>
  <td>20200110006</td>
  <td>timestamps</td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">module_address</a></strong></td>
  <td>524689a4f870c46d6a5d901b5ac1fdb2</td>
  <td>module address of violas swap(btc)</td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">out_amount</a></strong></td>
  <td>1000000</td>
  <td>swap violas btc token amount microamount(1000000) </td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">times</a></strong></td>
  <td>0</td>
  <td>retry swap violas btc token number of times</td>
 </tr>
</table>

```
hex-Vstr: 6a3c76696f6c617300035002c91806cabcd5b2b5fa25ae1c50bed3c600000004b40537b6524689a4f870c46d6a5d901b5ac1fdb200000000000027100000

fields:
    OP_RETURN head:
        6a : OP_RETURN(0x6a)
        3c : data len(60)
    payload datas:
        76696f6c6173 : mark(violas)
        0003 : version(0x0003)
        5002 : type(0x5002)
        c91806cabcd5b2b5fa25ae1c50bed3c6 : payee_address
        00000004b40537b6 : sequence(20200110006)
        524689a4f870c46d6a5d901b5ac1fdb2 : module_address
        0000000000002710 : out_amount(10000)
        0000:times(0)
```

### swap libra gbp - start

**Description**

btc swap libra token(gbp) request


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Versions---type">version</a></strong></td>
  <td>0x0003</td>
  <td></td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>0x5003</td>
  <td></td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">payee_address</a></strong></td>
  <td>c91806cabcd5b2b5fa25ae1c50bed3c6</td>
  <td>payee address</td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">sequence</a></strong></td>
  <td>20200110006</td>
  <td>timestamps</td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">module_address</a></strong></td>
  <td>524689a4f870c46d6a5d901b5ac1fdb2</td>
  <td>module address of violas swap(btc)</td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">out_amount</a></strong></td>
  <td>1000000</td>
  <td>swap violas btc token amount microamount(1000000) </td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">times</a></strong></td>
  <td>0</td>
  <td>retry swap violas btc token number of times</td>
 </tr>
</table>

```
hex-Vstr: 6a3c76696f6c617300035003c91806cabcd5b2b5fa25ae1c50bed3c600000004b40537b6524689a4f870c46d6a5d901b5ac1fdb200000000000027100000

fields:
    OP_RETURN head:
        6a : OP_RETURN(0x6a)
        3c : data len(60)
    payload datas:
        76696f6c6173 : mark(violas)
        0003 : version(0x0003)
        5003 : type(0x5003)
        c91806cabcd5b2b5fa25ae1c50bed3c6 : payee_address
        00000004b40537b6 : sequence(20200110006)
        524689a4f870c46d6a5d901b5ac1fdb2 : module_address
        0000000000002710 : out_amount(10000)
        0000:times(0)
```

