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
  <td><strong>violas_address</strong></td>
  <td>char(32)</td>
  <td>auth_key_prefix:16 + address:16</td>
 </tr>
 <tr>
  <td><strong>sequence</strong></td>
  <td>uint64</td>
  <td>big-endian</td>
  <td>transaction sequence. ex: timestamps </td>
 </tr>
 <tr>
  <td><strong>module_address</strong></td>
  <td>char(32)</td>
  <td>auth_key_prefix:16 + address:16</td>
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
  <td>request mapping violas token</td>
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
</table>




---




## Payloads 

**Description**

btc transaction's OP_RETURN datas



### mapping - start

**Description**

btc mapping violas token request


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Versions---type">version</a></strong></td>
  <td>0x0000</td>
  <td></td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>0x3000</td>
  <td></td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">violas_address</a></strong></td>
  <td>f086b6a2348ac502c708ac41d06fe824c91806cabcd5b2b5fa25ae1c50bed3c6</td>
  <td>payee address</td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">sequence</a></strong></td>
  <td>20200110006</td>
  <td>timestamps</td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">module_address</a></strong></td>
  <td>cd0476e85ecc5fa71b61d84b9cf2f7fd524689a4f870c46d6a5d901b5ac1fdb2</td>
  <td>module address of violas tokens(vlsbtc)</td>
 </tr>
</table>

```
hex-Vstr: 6a4c5276696f6c617300003000f086b6a2348ac502c708ac41d06fe824c91806cabcd5b2b5fa25ae1c50bed3c600000004b40537b6cd0476e85ecc5fa71b61d84b9cf2f7fd524689a4f870c46d6a5d901b5ac1fdb2

fields:
    OP_RETURN head:
        6a : OP_RETURN(0x6a)
        4c : OP_PUSHDATA1(0x4c)
        52 : data len(82)
    payload datas:
        76696f6c6173 : mark(violas)
        0000 : version(0x0000)
        3000 : type(0x3000)
        f086b6a2348ac502c708ac41d06fe824c91806cabcd5b2b5fa25ae1c50bed3c6 : violas_address
        00000004b40537b6 : sequence(20200110006)
        cd0476e85ecc5fa71b61d84b9cf2f7fd524689a4f870c46d6a5d901b5ac1fdb2 : module_address
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
  <td>0x0000</td>
  <td></td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>0x3001</td>
  <td></td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">violas_address</a></strong></td>
  <td>f086b6a2348ac502c708ac41d06fe824c91806cabcd5b2b5fa25ae1c50bed3c6</td>
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
hex-Vstr: 6a4376696f6c617300003001f086b6a2348ac502c708ac41d06fe824c91806cabcd5b2b5fa25ae1c50bed3c600000004b40537b60000000000002710000000000000271A

fields:
    OP_RETURN head:
        6a : OP_RETURN(0x6a)
        43 : data len(67)
    payload datas:
        76696f6c6173 : mark(violas)
        0000 : version(0x0000)
        3001 : type(0x3001)
        f086b6a2348ac502c708ac41d06fe824c91806cabcd5b2b5fa25ae1c50bed3c6 : violas_address
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
  <td>0x0000</td>
  <td></td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>0x1030</td>
  <td></td>
 </tr>
 <tr>
  <td><strong><a href="#Fields---type">violas_address</a></strong></td>
  <td>f086b6a2348ac502c708ac41d06fe824c91806cabcd5b2b5fa25ae1c50bed3c6</td>
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
hex-Vstr: 6a4276696f6c617300001030f086b6a2348ac502c708ac41d06fe824c91806cabcd5b2b5fa25ae1c50bed3c600000004b40537b6000000000000271076696f6c617300

fields:
    OP_RETURN head:
        6a : OP_RETURN(0x6a)
        42 : data len(66)
    payload datas:
        76696f6c6173 : mark(violas)
        0000 : version(0x0000)
        1030 : type(0x1030)
        f086b6a2348ac502c708ac41d06fe824c91806cabcd5b2b5fa25ae1c50bed3c6 : violas_address
        00000004b40537b6 : sequence(20200110006)
        000000000002710 : btc_amount(10000)
        76696f6c617300 : mark_name(violas + '\0')
``` 
