# CONTENT

**Note**: The Mapping Protocol Specification is under development and may be updated in the future.

## Overview

Mapping Protocol is based on the [JSON](https://www.json.org/json-en.html) formats.This Specification defines the mapping types, and provides usage examples.

## Version

v2.0.0

## JSON 
JSON (JavaScript Object Notation) is a lightweight data-interchange format, It is easy for humans to read and write. It is easy for machines to parse and generate. Refer to the [JSON](https://www.json.org/json-en.html)



---



## Flags - type

**Description**

Describe the chain type to which the transaction belongs

### Attributes

<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong>violas</strong></td>
  <td>string</td>
  <td>transaction is in violas chain</td>
 </tr>
 <tr>
  <td><strong>libra</strong></td>
  <td>string</td>
  <td>transaction is in libra chain</td>
 </tr>
 <tr>
  <td><strong>ethereum</strong></td>
  <td>string</td>
  <td>transaction is in ethereum chain</td>
 </tr>
</table>


## Types - type

**Description**

The type of transaction mapping, l2vxxx is to map stablecoins from violas chain from stablecoins on libra chain, v2lxxx is to map stablecoins from libra chain from stablecoins from violals。


### Attributes


<table>
  <tr>
   <td><strong>Name</strong></td>
   <td><strong>Type</strong></td>
   <td><strong>Description</strong></td>
  </tr>
  <tr>
   <td><strong>l2vusd</strong></td>
   <td>string</td>
   <td>libra's stable coin(any token) mapping to violas‘s stable coin VLSUSD.</td>
  </tr>
  <tr>
   <td><strong>l2vgbp</strong></td>
   <td>string</td>
   <td>libra's stable coin(any token) mapping to violas‘s stable coin VLSGBP.</td>
  </tr>
  <tr>
   <td><strong>l2veur</strong></td>
   <td>string</td>
   <td>libra's stable coin(any token) mapping to violas‘s stable coin VLSEUR.</td>
  </tr>
  <tr>
   <td><strong>l2vjpy</strong></td>
   <td>string</td>
   <td>libra's stable coin(any token) mapping to violas‘s stable coin VLSJPY.</td>
  </tr>
  <tr>
   <td><strong>l2vsgd</strong></td>
   <td>string</td>
   <td>libra's stable coin(any token) mapping to violas‘s stable coin VLSSGD.</td>
  </tr>
  <tr>
   <td><strong>v2lusd</strong></td>
   <td>string</td>
   <td>liolas's stable coin(any token) mapping to libra‘s stable coin ≋USD.</td>
  </tr>
  <tr>
   <td><strong>v2lgbp</strong></td>
   <td>string</td>
   <td>violas's stable coin(any token) mapping to libra‘s stable coin ≋GBP.</td>
  </tr>
  <tr>
   <td><strong>v2leur</strong></td>
   <td>string</td>
   <td>violas's stable coin(any token) mapping to libra‘s stable coin ≋EUR.</td>
  </tr>
  <tr>
   <td><strong>v2ljpy</strong></td>
   <td>string</td>
   <td>violas's stable coin(any token) mapping to libra‘s stable coin ≋JPY.</td>
  </tr>
  <tr>
   <td><strong>v2lsgd</strong></td>
   <td>string</td>
   <td>violas's stable coin(any token) mapping to libra‘s stable coin ≋SGD.</td>
  </tr>
  <tr>
   <td><strong>v2b</strong></td>
   <td>string</td>
   <td>violas stable token(any token) swap to btc</td>
  </tr>
  <tr>
   <td><strong>l2b</strong></td>
   <td>string</td>
   <td>libra stable token(any token) swap to btc</td>
  </tr>
  <tr>
   <td><strong>v2bm</strong></td>
   <td>string</td>
   <td>violas btc token reflection to bitcoin btc. ratio: 1:1</td>
  </tr>
  <tr>
   <td><strong>v2lm</strong></td>
   <td>string</td>
   <td>violas map token(any token) reflection to libra stable token. ratio: 1:1</td>
  </tr>
  <tr>
   <td><strong>l2vm</strong></td>
   <td>string</td>
   <td>libra stable token(any token) swap to violas mapping token. ratio : 1:1</td>
  </tr>
  <tr>
   <td><strong>v2em</strong></td>
   <td>string</td>
   <td>violas map token reflection to ethereum erc20 token. ratio: 1:1</td>
  </tr>
  <tr>
   <td><strong>funds</strong></td>
   <td>string</td>
   <td>request funding from manager</td>
  </tr>
</table>


## States - type

**Description**

Transaction request type

### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong>start</strong></td>
  <td>string</td>
  <td>request mapping</td>
 </tr>
 <tr>
  <td><strong>end</strong></td>
  <td>string</td>
  <td>mapping completed</td>
 </tr>
 <tr>
  <td><strong>cancel</strong></td>
  <td>string</td>
  <td>mapping cancel(user execute), repay coin to payer</td>
 </tr>
 <tr>
  <td><strong>stop</strong></td>
  <td>string</td>
  <td>mapping stop(server execute), repay coin to payer</td>
 </tr>
</table>


## Keys - type

**Description**

Keys in JSON string

### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Flags---type">flag</a></strong></td>
  <td>string</td>
  <td>Differentiate transactions on different chains</td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>string</td>
  <td>Distinguish between different mapping types</td>
 </tr>
 <tr>
  <td><strong>to_address</strong></td>
  <td>string</td>
  <td>Payee Address</td>
 </tr>
 <tr>
  <td><strong>tran_id</strong></td>
  <td>string</td>
  <td>hex-str(len=64), Generate tran_id based on the transaction information of the starting state</td>
 </tr>
 <tr>
  <td><strong><a href="#States---type">state</a></strong></td>
  <td>string</td>
  <td>Transaction request type</td>
 </tr>
 <tr>
  <td><strong>out_amount</strong></td>
  <td>uint64</td>
  <td>exchange quantity</td>
 </tr>
 <tr>
  <td><strong>times</strong></td>
  <td>uint64</td>
  <td>exchange times, 0:always n(n>0): n times</td>
 </tr>
</table>




---




## payload

**Description**



### l2vusd - start

**Description**

≋USD Mapping LBRUSD


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Flags---type">flag</a></strong></td>
  <td>string</td>
  <td>libra</td>
  <td>Differentiate transactions on different chains</td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>string</td>
  <td>l2vusd</td>
  <td>Distinguish between different mapping types</td>
 </tr>
 <tr>
  <td><strong>to_address</strong></td>
  <td>string</td>
  <td>violas address:00000000000000000000000000000000 + address for hex-str(len = 32)</td>
  <td>Payee Address</td>
 </tr>
 <tr>
  <td><strong><a href="#States---type">state</a></strong></td>
  <td>string</td>
  <td>start</td>
  <td>Transaction request type</td>
 </tr>
 <tr>
  <td><strong>out_amount</strong></td>
  <td>uint64</td>
  <td>1~max(uint64)</td>
  <td>exchange quantity</td>
 </tr>
 <tr>
  <td><strong>times</strong></td>
  <td>uint64</td>
  <td>0~max(uint64)</td>
  <td>exchange execute times</td>
 </tr>
</table>

```
'{"flag":"libra", "type":"l2vusd", "times": 0, "to_address":"0000000000000000000000000000000059352b2c39bec33a880ae1334bea8129", "out_amount": 1000000", state":"start"}'
```


### l2vusd - end/cancel/stop

**Description**

≋USD Mapping LBRUSD complete


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Flags---type">flag</a></strong></td>
  <td>string</td>
  <td>libra</td>
  <td>Differentiate transactions on different chains</td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>string</td>
  <td>l2vusd</td>
  <td>Distinguish between different mapping types</td>
 </tr>
 <tr>
  <td><strong>tran_id</strong></td>
  <td>string</td>
  <td>hex-str(len = 64)</td>
  <td>The tran_id corresponding to the transaction to be modified</td>
 </tr>
 <tr>
  <td><strong><a href="#States---type">state</a></strong></td>
  <td>string</td>
  <td>end/cancel/stop</td>
  <td>Mapping completed</td>
 </tr>
</table>

```
'{"flag":"libra", "type":"l2vusd", "tran_id":"253896506a16795e895cb19429b569a2ca56ff5f37cb637032acd78c8a6fb588", "state":"end/cancel/stop"}'
```


### l2vgbp - start

**Description**

≋GBP Mapping LBRGBP


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Flags---type">flag</a></strong></td>
  <td>string</td>
  <td>libra</td>
  <td>Differentiate transactions on different chains</td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>string</td>
  <td>l2vgbp</td>
  <td>Distinguish between different mapping types</td>
 </tr>
 <tr>
  <td><strong>to_address</strong></td>
  <td>string</td>
  <td>violas address:00000000000000000000000000000000 + address for hex-str(len = 32)</td>
  <td>Payee Address</td>
 </tr>
 <tr>
  <td><strong><a href="#States---type">state</a></strong></td>
  <td>string</td>
  <td>start</td>
  <td>Transaction request type</td>
 </tr>
 <tr>
  <td><strong>out_amount</strong></td>
  <td>uint64</td>
  <td>1~max(uint64)</td>
  <td>exchange quantity</td>
 </tr>
 <tr>
  <td><strong>times</strong></td>
  <td>uint64</td>
  <td>0~max(uint64)</td>
  <td>exchange execute times</td>
 </tr>
</table>

```
'{"flag":"libra", "type":"l2vgbp", "times": 0, "to_address":"0000000000000000000000000000000059352b2c39bec33a880ae1334bea8129", "out_amount": 1000000, "state":"start"}'
```


### l2vgbp - end/cancel/stop

**Description**

≋GBP Mapping LBRGBP complete


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Flags---type">flag</a></strong></td>
  <td>string</td>
  <td>libra</td>
  <td>Differentiate transactions on different chains</td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>string</td>
  <td>l2vgbp</td>
  <td>Distinguish between different mapping types</td>
 </tr>
 <tr>
  <td><strong>tran_id</strong></td>
  <td>string</td>
  <td>hex-str(len = 64)</td>
  <td>The tran_id corresponding to the transaction to be modified</td>
 </tr>
 <tr>
  <td><strong><a href="#States---type">state</a></strong></td>
  <td>string</td>
  <td>end/cancel/stop</td>
  <td>Mapping completed</td>
 </tr>
</table>

```
'{"flag":"libra", "type":"l2vgbp", "tran_id":"253896506a16795e895cb19429b569a2ca56ff5f37cb637032acd78c8a6fb588", "state": "end/cancel/stop"}'
```


### l2veur - start

**Description**

≋EUR Mapping LBREUR


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Flags---type">flag</a></strong></td>
  <td>string</td>
  <td>libra</td>
  <td>Differentiate transactions on different chains</td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>string</td>
  <td>l2veur</td>
  <td>Distinguish between different mapping types</td>
 </tr>
 <tr>
  <td><strong>to_address</strong></td>
  <td>string</td>
  <td>violas address:00000000000000000000000000000000 + address for hex-str(len = 32)</td>
  <td>Payee Address</td>
 </tr>
 <tr>
  <td><strong><a href="#States---type">state</a></strong></td>
  <td>string</td>
  <td>start</td>
  <td>Transaction request type</td>
 </tr>
 <tr>
  <td><strong>out_amount</strong></td>
  <td>uint64</td>
  <td>1~max(uint64)</td>
  <td>exchange quantity</td>
 </tr>
</table>

```
'{"flag":"libra", "type":"l2veur", "times": 0, "to_address":"0000000000000000000000000000000059352b2c39bec33a880ae1334bea8129", "out_amount": 1000000, "state":"start"}'
```


### l2veur - end/cancel/stop

**Description**

≋EUR Mapping LBREUR complete


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Flags---type">flag</a></strong></td>
  <td>string</td>
  <td>libra</td>
  <td>Differentiate transactions on different chains</td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>string</td>
  <td>l2veur</td>
  <td>Distinguish between different mapping types</td>
 </tr>
 <tr>
  <td><strong>tran_id</strong></td>
  <td>string</td>
  <td>hex-str(len = 64)</td>
  <td>The tran_id corresponding to the transaction to be modified</td>
 </tr>
 <tr>
  <td><strong><a href="#States---type">state</a></strong></td>
  <td>string</td>
  <td>end/cancel/stop</td>
  <td>Mapping completed</td>
 </tr>
</table>

```
'{"flag":"libra", "type":"l2veur", "tran_id":"253896506a16795e895cb19429b569a2ca56ff5f37cb637032acd78c8a6fb588", "state":"end/cancel/stop"}'
```


### l2vjpy - start

**Description**

≋JPY Mapping LBRJPY


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Flags---type">flag</a></strong></td>
  <td>string</td>
  <td>libra</td>
  <td>Differentiate transactions on different chains</td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>string</td>
  <td>l2vjpy</td>
  <td>Distinguish between different mapping types</td>
 </tr>
 <tr>
  <td><strong>to_address</strong></td>
  <td>string</td>
  <td>violas address:00000000000000000000000000000000 + address for hex-str(len = 32)</td>
  <td>Payee Address</td>
 </tr>
 <tr>
  <td><strong><a href="#States---type">state</a></strong></td>
  <td>string</td>
  <td>start</td>
  <td>Transaction request type</td>
 </tr>
 <tr>
  <td><strong>out_amount</strong></td>
  <td>uint64</td>
  <td>1~max(uint64)</td>
  <td>exchange quantity</td>
 </tr>
 <tr>
  <td><strong>times</strong></td>
  <td>uint64</td>
  <td>0~max(uint64)</td>
  <td>exchange execute times</td>
 </tr>
</table>

```
'{"flag":"libra", "type":"l2vjpy", "times": 0, "to_address":"0000000000000000000000000000000059352b2c39bec33a880ae1334bea8129", "out_amount": 1000000, "state":"start"}'
```


### l2vjpy - end/cancel/stop

**Description**

≋EUR Mapping LBREUR complete


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Flags---type">flag</a></strong></td>
  <td>string</td>
  <td>libra</td>
  <td>Differentiate transactions on different chains</td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>string</td>
  <td>l2vjpy</td>
  <td>Distinguish between different mapping types</td>
 </tr>
 <tr>
  <td><strong>tran_id</strong></td>
  <td>string</td>
  <td>hex-str(len = 64)</td>
  <td>The tran_id corresponding to the transaction to be modified</td>
 </tr>
 <tr>
  <td><strong><a href="#States---type">state</a></strong></td>
  <td>string</td>
  <td>end/cancel/stop</td>
  <td>Mapping completed</td>
 </tr>
</table>

```
'{"flag":"libra", "type":"l2vjpy", "tran_id":"253896506a16795e895cb19429b569a2ca56ff5f37cb637032acd78c8a6fb588", "state":"end/cancel/stop"}'
```


### l2vsgd - start

**Description**

≋SGD Mapping LBRSGD


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Flags---type">flag</a></strong></td>
  <td>string</td>
  <td>libra</td>
  <td>Differentiate transactions on different chains</td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>string</td>
  <td>l2vsgd</td>
  <td>Distinguish between different mapping types</td>
 </tr>
 <tr>
  <td><strong>to_address</strong></td>
  <td>string</td>
  <td>violas address:00000000000000000000000000000000 + address for hex-str(len = 32)</td>
  <td>Payee Address</td>
 </tr>
 <tr>
  <td><strong><a href="#States---type">state</a></strong></td>
  <td>string</td>
  <td>start</td>
  <td>Transaction request type</td>
 </tr>
 <tr>
  <td><strong>out_amount</strong></td>
  <td>uint64</td>
  <td>1~max(uint64)</td>
  <td>exchange quantity</td>
 </tr>
 <tr>
  <td><strong>times</strong></td>
  <td>uint64</td>
  <td>0~max(uint64)</td>
  <td>exchange execute times</td>
 </tr>
</table>

```
'{"flag":"libra", "type":"l2vsgd", "times": 0, "to_address":"0000000000000000000000000000000059352b2c39bec33a880ae1334bea8129", "out_amount": 1000000, "state":"start"}'
```


### l2vsgd - end/cancel/stop

**Description**

≋SGD Mapping LBRSGD complete


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Flags---type">flag</a></strong></td>
  <td>string</td>
  <td>libra</td>
  <td>Differentiate transactions on different chains</td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>string</td>
  <td>l2vsgd</td>
  <td>Distinguish between different mapping types</td>
 </tr>
 <tr>
  <td><strong>tran_id</strong></td>
  <td>string</td>
  <td>hex-str(len = 64)</td>
  <td>The tran_id corresponding to the transaction to be modified</td>
 </tr>
 <tr>
  <td><strong><a href="#States---type">state</a></strong></td>
  <td>string</td>
  <td>end/cancel/stop</td>
  <td>Mapping completed</td>
 </tr>
</table>

```
'{"flag":"libra", "type":"l2vsgd", "tran_id":"253896506a16795e895cb19429b569a2ca56ff5f37cb637032acd78c8a6fb588", "state":"end/cancel/stop"}'
```


### v2lusd - start

**Description**

LBRUSD Mapping ≋USD 


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Flags---type">flag</a></strong></td>
  <td>string</td>
  <td>violas</td>
  <td>Differentiate transactions on different chains</td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>string</td>
  <td>v2lusd</td>
  <td>Distinguish between different mapping types</td>
 </tr>
 <tr>
  <td><strong>to_address</strong></td>
  <td>string</td>
  <td>libra address:00000000000000000000000000000000 + address for hex-str(len = 32)</td>
  <td>Payee Address</td>
 </tr>
 <tr>
  <td><strong><a href="#States---type">state</a></strong></td>
  <td>string</td>
  <td>start</td>
  <td>Transaction request type</td>
 </tr>
 <tr>
  <td><strong>out_amount</strong></td>
  <td>uint64</td>
  <td>1~max(uint64)</td>
  <td>exchange quantity</td>
 </tr>
 <tr>
  <td><strong>times</strong></td>
  <td>uint64</td>
  <td>0~max(uint64)</td>
  <td>exchange execute times</td>
 </tr>
</table>

```
'{"flag":"violas", "type":"v2lusd", "times": 0, "to_address":"0000000000000000000000000000000059352b2c39bec33a880ae1334bea8129", "out_amount": 1000000, "state":"start"}'
```


### v2lusd - end/cancel/stop

**Description**

LBRUSD Mapping ≋USD completed


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Flags---type">flag</a></strong></td>
  <td>string</td>
  <td>violas</td>
  <td>Differentiate transactions on different chains</td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>string</td>
  <td>v2lusd</td>
  <td>Distinguish between different mapping types</td>
 </tr>
 <tr>
  <td><strong>tran_id</strong></td>
  <td>string</td>
  <td>hex-str(len = 64)</td>
  <td>The tran_id corresponding to the transaction to be modified</td>
 </tr>
 <tr>
  <td><strong><a href="#States---type">state</a></strong></td>
  <td>string</td>
  <td>end/cancel/stop</td>
  <td>Mapping completed</td>
 </tr>
</table>

```
'{"flag":"violas", "type":"v2lusd", "tran_id":"253896506a16795e895cb19429b569a2ca56ff5f37cb637032acd78c8a6fb588", "state":"end/cancel/stop"}'
```


### v2lgbp - start

**Description**

LBRGBP Mapping ≋GBP


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Flags---type">flag</a></strong></td>
  <td>string</td>
  <td>violas</td>
  <td>Differentiate transactions on different chains</td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>string</td>
  <td>v2lgbp</td>
  <td>Distinguish between different mapping types</td>
 </tr>
 <tr>
  <td><strong>to_address</strong></td>
  <td>string</td>
  <td>libra address:00000000000000000000000000000000 + address for hex-str(len = 32)</td>
  <td>Payee Address</td>
 </tr>
 <tr>
  <td><strong><a href="#States---type">state</a></strong></td>
  <td>string</td>
  <td>start</td>
  <td>Transaction request type</td>
 </tr>
 <tr>
  <td><strong>out_amount</strong></td>
  <td>uint64</td>
  <td>1~max(uint64)</td>
  <td>exchange quantity</td>
 </tr>
 <tr>
  <td><strong>times</strong></td>
  <td>uint64</td>
  <td>0~max(uint64)</td>
  <td>exchange execute times</td>
 </tr>
</table>

```
'{"flag":"violas", "type":"v2lgbp", "times": 0, "to_address":"0000000000000000000000000000000059352b2c39bec33a880ae1334bea8129", "out_amount": 1000000, "state":"start"}'
```


### v2lgbp - end/cancel/stop

**Description**

LBRGBP Mapping ≋GBP completed


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Flags---type">flag</a></strong></td>
  <td>string</td>
  <td>violas</td>
  <td>Differentiate transactions on different chains</td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>string</td>
  <td>v2lgbp</td>
  <td>Distinguish between different mapping types</td>
 </tr>
 <tr>
  <td><strong>tran_id</strong></td>
  <td>string</td>
  <td>hex-str(len = 64)</td>
  <td>The tran_id corresponding to the transaction to be modified</td>
 </tr>
 <tr>
  <td><strong><a href="#States---type">state</a></strong></td>
  <td>string</td>
  <td>end/cancel/stop</td>
  <td>Mapping completed</td>
 </tr>
</table>

```
'{"flag":"violas", "type":"v2lgbp", "tran_id":"253896506a16795e895cb19429b569a2ca56ff5f37cb637032acd78c8a6fb588", "state":"end/cancel/stop"}'
```


### v2leur - start

**Description**

LBREUR Mapping ≋EUR


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Flags---type">flag</a></strong></td>
  <td>string</td>
  <td>violas</td>
  <td>Differentiate transactions on different chains</td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>string</td>
  <td>v2leur</td>
  <td>Distinguish between different mapping types</td>
 </tr>
 <tr>
  <td><strong>to_address</strong></td>
  <td>string</td>
  <td>libra address:00000000000000000000000000000000 + address for hex-str(len = 32)</td>
  <td>Payee Address</td>
 </tr>
 <tr>
  <td><strong><a href="#States---type">state</a></strong></td>
  <td>string</td>
  <td>start</td>
  <td>Transaction request type</td>
 </tr>
 <tr>
  <td><strong>out_amount</strong></td>
  <td>uint64</td>
  <td>1~max(uint64)</td>
  <td>exchange quantity</td>
 </tr>
 <tr>
  <td><strong>times</strong></td>
  <td>uint64</td>
  <td>0~max(uint64)</td>
  <td>exchange execute times</td>
 </tr>
</table>

```
'{"flag":"violas", "type":"v2leur", "times": 0, "to_address":"0000000000000000000000000000000059352b2c39bec33a880ae1334bea8129", "out_amount": 1000000, "state":"start"}'
```


### v2leur - end/cancel/stop

**Description**

LBREUR Mapping ≋EUR completed


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Flags---type">flag</a></strong></td>
  <td>string</td>
  <td>violas</td>
  <td>Differentiate transactions on different chains</td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>string</td>
  <td>v2leur</td>
  <td>Distinguish between different mapping types</td>
 </tr>
 <tr>
  <td><strong>tran_id</strong></td>
  <td>string</td>
  <td>hex-str(len = 64)</td>
  <td>The tran_id corresponding to the transaction to be modified</td>
 </tr>
 <tr>
  <td><strong><a href="#States---type">state</a></strong></td>
  <td>string</td>
  <td>end/cancel/stop</td>
  <td>Mapping completed</td>
 </tr>
</table>

```
'{"flag":"violas", "type":"v2leur", "tran_id":"253896506a16795e895cb19429b569a2ca56ff5f37cb637032acd78c8a6fb588", "state":"end/cancel/stop"}'
```


### v2ljpy - start

**Description**

LBRJPY Mapping ≋JPY


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Flags---type">flag</a></strong></td>
  <td>string</td>
  <td>violas</td>
  <td>Differentiate transactions on different chains</td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>string</td>
  <td>v2ljpy</td>
  <td>Distinguish between different mapping types</td>
 </tr>
 <tr>
  <td><strong>to_address</strong></td>
  <td>string</td>
  <td>libra address:00000000000000000000000000000000 + address for hex-str(len = 32)</td>
  <td>Payee Address</td>
 </tr>
 <tr>
  <td><strong><a href="#States---type">state</a></strong></td>
  <td>string</td>
  <td>start</td>
  <td>Transaction request type</td>
 </tr>
 <tr>
  <td><strong>out_amount</strong></td>
  <td>uint64</td>
  <td>1~max(uint64)</td>
  <td>exchange quantity</td>
 </tr>
 <tr>
  <td><strong>times</strong></td>
  <td>uint64</td>
  <td>0~max(uint64)</td>
  <td>exchange execute times</td>
 </tr>
</table>

```
'{"flag":"violas", "type":"v2ljpy", "times": 0, "to_address":"0000000000000000000000000000000059352b2c39bec33a880ae1334bea8129", "out_amount": 1000000, "state":"start"}'
```


### v2ljpy - end/cancel/stop

**Description**

LBREUR Mapping ≋EUR completed


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Flags---type">flag</a></strong></td>
  <td>string</td>
  <td>violas</td>
  <td>Differentiate transactions on different chains</td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>string</td>
  <td>v2ljpy</td>
  <td>Distinguish between different mapping types</td>
 </tr>
 <tr>
  <td><strong>tran_id</strong></td>
  <td>string</td>
  <td>hex-str(len = 64)</td>
  <td>The tran_id corresponding to the transaction to be modified</td>
 </tr>
 <tr>
  <td><strong><a href="#States---type">state</a></strong></td>
  <td>string</td>
  <td>end/cancel/stop</td>
  <td>Mapping completed</td>
 </tr>
</table>

```
'{"flag":"violas", "type":"v2ljpy", "tran_id":"253896506a16795e895cb19429b569a2ca56ff5f37cb637032acd78c8a6fb588", "state":"end/cancel/stop"}'
```


### v2lsgd - start

**Description**

LBRSGD Mapping ≋SGD


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Flags---type">flag</a></strong></td>
  <td>string</td>
  <td>violas</td>
  <td>Differentiate transactions on different chains</td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>string</td>
  <td>v2lsgd</td>
  <td>Distinguish between different mapping types</td>
 </tr>
 <tr>
  <td><strong>to_address</strong></td>
  <td>string</td>
  <td>libra address:00000000000000000000000000000000 + address for hex-str(len = 32)</td>
  <td>Payee Address</td>
 </tr>
 <tr>
  <td><strong><a href="#States---type">state</a></strong></td>
  <td>string</td>
  <td>start</td>
  <td>Transaction request type</td>
 </tr>
 <tr>
  <td><strong>out_amount</strong></td>
  <td>uint64</td>
  <td>1~max(uint64)</td>
  <td>exchange quantity</td>
 </tr>
 <tr>
  <td><strong>times</strong></td>
  <td>uint64</td>
  <td>0~max(uint64)</td>
  <td>exchange execute times</td>
 </tr>
</table>

```
'{"flag":"violas", "type":"v2lsgd", "times": 0, "to_address":"0000000000000000000000000000000059352b2c39bec33a880ae1334bea8129", "out_amount": 1000000, "state":"start"}'
```


### v2lsgd - end/cancel/stop

**Description**

LBRSGD Mapping ≋SGD completed


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Flags---type">flag</a></strong></td>
  <td>string</td>
  <td>violas</td>
  <td>Differentiate transactions on different chains</td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>string</td>
  <td>v2lsgd</td>
  <td>Distinguish between different mapping types</td>
 </tr>
 <tr>
  <td><strong>tran_id</strong></td>
  <td>string</td>
  <td>hex-str(len = 64)</td>
  <td>The tran_id corresponding to the transaction to be modified</td>
 </tr>
 <tr>
  <td><strong><a href="#States---type">state</a></strong></td>
  <td>string</td>
  <td>end/cancel/stop</td>
  <td>Mapping completed</td>
 </tr>
</table>

```
'{"flag":"violas", "type":"v2lsgd", "tran_id":"253896506a16795e895cb19429b569a2ca56ff5f37cb637032acd78c8a6fb588", "state":"end/cancel/stop"}'
```

### v2b - start

**Description**

violas token map to btc


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Flags---type">flag</a></strong></td>
  <td>string</td>
  <td>violas</td>
  <td>Differentiate transactions on different chains</td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>string</td>
  <td>v2b</td>
  <td>Distinguish between different mapping types</td>
 </tr>
 <tr>
  <td><strong>to_address</strong></td>
  <td>string</td>
  <td>hex-str(btc address)</td>
  <td>Payee Address</td>
 </tr>
 <tr>
  <td><strong><a href="#States---type">state</a></strong></td>
  <td>string</td>
  <td>start</td>
  <td>Mapping</td>
 </tr>
 <tr>
  <td><strong>out_amount</strong></td>
  <td>uint64</td>
  <td>1~max(uint64)</td>
  <td>exchange quantity</td>
 </tr>
 <tr>
  <td><strong>times</strong></td>
  <td>uint64</td>
  <td>0~max(uint64)</td>
  <td>exchange execute times</td>
 </tr>
</table>

```
'{"flag":"violas", "type":"v2b", "times": 0, "to_address":"2MxBZG7295wfsXaUj69quf8vucFzwG35UWh", "out_amount": 1000000, "state":"start"}'
```


### v2b - end/cancel/stop

**Description**

BTC swap end/cancel/stop


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Flags---type">flag</a></strong></td>
  <td>string</td>
  <td>violas</td>
  <td>Differentiate transactions on different chains</td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>string</td>
  <td>v2b</td>
  <td>Distinguish between different mapping types</td>
 </tr>
 <tr>
  <td><strong>tran_id</strong></td>
  <td>string</td>
  <td>hex-str</td>
  <td>The tran_id corresponding to the transaction to be modified</td>
 </tr>
 <tr>
  <td><strong><a href="#States---type">state</a></strong></td>
  <td>string</td>
  <td>end/cancel/stop</td>
  <td>Mapping completed</td>
 </tr>
</table>

```
'{"flag":"violas", "type":"v2b", "tran_id":"253896506a16795e895cb19429b569a2ca56ff5f37cb637032acd78c8a6fb588", "state":"end/cancel/stop"}'
```

### l2b - start

**Description**

libra token map to btc


#### Attributes

<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Flags---type">flag</a></strong></td>
  <td>string</td>
  <td>libra</td>
  <td>Differentiate transactions on different chains</td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>string</td>
  <td>l2b</td>
  <td>Distinguish between different mapping types</td>
 </tr>
 <tr>
  <td><strong>to_address</strong></td>
  <td>string</td>
  <td>hex-str(btc address)</td>
  <td>Payee Address</td>
 </tr>
 <tr>
  <td><strong><a href="#States---type">state</a></strong></td>
  <td>string</td>
  <td>start</td>
  <td>Mapping</td>
 </tr>
 <tr>
  <td><strong>out_amount</strong></td>
  <td>uint64</td>
  <td>1~max(uint64)</td>
  <td>exchange quantity</td>
 </tr>
 <tr>
  <td><strong>times</strong></td>
  <td>uint64</td>
  <td>0~max(uint64)</td>
  <td>exchange execute times</td>
 </tr>
</table>

```
'{"flag":"libra", "type":"l2b", "times": 0, "to_address":"2MxBZG7295wfsXaUj69quf8vucFzwG35UWh", "out_amount": 1000000, "state":"start"}'
```


### l2b - end/cancel/stop

**Description**

swap end/cancel/stop


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Flags---type">flag</a></strong></td>
  <td>string</td>
  <td>libra</td>
  <td>Differentiate transactions on different chains</td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>string</td>
  <td>l2b</td>
  <td>Distinguish between different mapping types</td>
 </tr>
 <tr>
  <td><strong>tran_id</strong></td>
  <td>string</td>
  <td>hex-str</td>
  <td>The tran_id corresponding to the transaction to be modified</td>
 </tr>
 <tr>
  <td><strong><a href="#States---type">state</a></strong></td>
  <td>string</td>
  <td>end/cancel/stop</td>
  <td>Mapping completed</td>
 </tr>
</table>

```
'{"flag":"libra", "type":"l2b", "tran_id":"253896506a16795e895cb19429b569a2ca56ff5f37cb637032acd78c8a6fb588", "state":"end/cancel/stop"}'
```



### v2bm - start

**Description**

violas btc mapping to bitcoin btc


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Flags---type">flag</a></strong></td>
  <td>string</td>
  <td>violas</td>
  <td>Differentiate transactions on different chains</td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>string</td>
  <td>v2bm</td>
  <td>Distinguish between different mapping types</td>
 </tr>
 <tr>
  <td><strong>to_address</strong></td>
  <td>string</td>
  <td>hex-str(btc address)</td>
  <td>Payee Address</td>
 </tr>
 <tr>
  <td><strong><a href="#States---type">state</a></strong></td>
  <td>string</td>
  <td>start</td>
  <td>Mapping</td>
 </tr>
 <tr>
  <td><strong>times</strong></td>
  <td>uint64</td>
  <td>0~max(uint64)</td>
  <td>exchange execute times: 1</td>
 </tr>
</table>

```
'{"flag":"violas", "type":"v2bm", "times": 1, "to_address":"2MxBZG7295wfsXaUj69quf8vucFzwG35UWh", "state":"start"}'
```


### v2bm - end/cancel/stop

**Description**

BTC mapping end/cancel/stop


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Flags---type">flag</a></strong></td>
  <td>string</td>
  <td>violas</td>
  <td>Differentiate transactions on different chains</td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>string</td>
  <td>v2bm</td>
  <td>Distinguish between different mapping types</td>
 </tr>
 <tr>
  <td><strong>tran_id</strong></td>
  <td>string</td>
  <td>hex-str</td>
  <td>The tran_id corresponding to the transaction to be modified</td>
 </tr>
 <tr>
  <td><strong><a href="#States---type">state</a></strong></td>
  <td>string</td>
  <td>end/cancel/stop</td>
  <td>Mapping completed</td>
 </tr>
</table>

```
'{"flag":"violas", "type":"v2bm", "tran_id":"253896506a16795e895cb19429b569a2ca56ff5f37cb637032acd78c8a6fb588", "state":"end/cancel/stop"}'
```


### v2lm - start

**Description**

violas mapping-token to mapping libra stable token


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Flags---type">flag</a></strong></td>
  <td>string</td>
  <td>violas</td>
  <td>Differentiate transactions on different chains</td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>string</td>
  <td>v2lm</td>
  <td>Distinguish between different mapping types</td>
 </tr>
 <tr>
  <td><strong>to_address</strong></td>
  <td>string</td>
  <td>hex-str(libra address)</td>
  <td>Payee Address</td>
 </tr>
 <tr>
  <td><strong><a href="#States---type">state</a></strong></td>
  <td>string</td>
  <td>start</td>
  <td>Mapping</td>
 </tr>
 <tr>
  <td><strong>times</strong></td>
  <td>uint64</td>
  <td>0~max(uint64)</td>
  <td>exchange execute times: 1</td>
 </tr>
</table>

```
'{"flag":"violas", "type":"v2lm", "times": 1, "to_address":"50645a7cbc3e03ae70871de0a447c532", "state":"start"}'
```


### v2lm - end/cancel/stop

**Description**

violas mapping-token mapping libra stable token end/cancel/stop


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Flags---type">flag</a></strong></td>
  <td>string</td>
  <td>violas</td>
  <td>Differentiate transactions on different chains</td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>string</td>
  <td>v2lm</td>
  <td>Distinguish between different mapping types</td>
 </tr>
 <tr>
  <td><strong>tran_id</strong></td>
  <td>string</td>
  <td>hex-str</td>
  <td>The tran_id corresponding to the transaction to be modified</td>
 </tr>
 <tr>
  <td><strong><a href="#States---type">state</a></strong></td>
  <td>string</td>
  <td>end/cancel/stop</td>
  <td>Mapping completed</td>
 </tr>
</table>

```
'{"flag":"violas", "type":"v2lm", "tran_id":"253896506a16795e895cb19429b569a2ca56ff5f37cb637032acd78c8a6fb588", "state":"end/cancel/stop"}'
```


### l2vm - start

**Description**

libra stable token mapping violas mapping-token


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Flags---type">flag</a></strong></td>
  <td>string</td>
  <td>libra</td>
  <td>Differentiate transactions on different chains</td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>string</td>
  <td>l2vm</td>
  <td>Distinguish between different mapping types</td>
 </tr>
 <tr>
  <td><strong>to_address</strong></td>
  <td>string</td>
  <td>hex-str(violas address)</td>
  <td>Payee Address</td>
 </tr>
 <tr>
  <td><strong><a href="#States---type">state</a></strong></td>
  <td>string</td>
  <td>start</td>
  <td>Mapping</td>
 </tr>
 <tr>
  <td><strong>times</strong></td>
  <td>uint64</td>
  <td>0~max(uint64)</td>
  <td>exchange execute times: 1</td>
 </tr>
</table>

```
'{"flag":"libra", "type":"l2vm", "times": 1, "to_address":"50645a7cbc3e03ae70871de0a447c532", "state":"start"}'
```


### l2vm - end/cancel/stop

**Description**

libra stable token mapping violas mapping-token end/cancel/stop


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Flags---type">flag</a></strong></td>
  <td>string</td>
  <td>libra</td>
  <td>Differentiate transactions on different chains</td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>string</td>
  <td>l2vm</td>
  <td>Distinguish between different mapping types</td>
 </tr>
 <tr>
  <td><strong>tran_id</strong></td>
  <td>string</td>
  <td>hex-str</td>
  <td>The tran_id corresponding to the transaction to be modified</td>
 </tr>
 <tr>
  <td><strong><a href="#States---type">state</a></strong></td>
  <td>string</td>
  <td>end/cancel/stop</td>
  <td>Mapping completed</td>
 </tr>
</table>

```
'{"flag":"libra", "type":"l2vm", "tran_id":"253896506a16795e895cb19429b569a2ca56ff5f37cb637032acd78c8a6fb588", "state":"end/cancel/stop"}'
```

### v2em - start

**Description**

ethereum erc20 token mapping violas mapping-token


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Flags---type">flag</a></strong></td>
  <td>string</td>
  <td>violas</td>
  <td>Differentiate transactions on different chains</td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>string</td>
  <td>v2em</td>
  <td>Distinguish between different mapping types</td>
 </tr>
 <tr>
  <td><strong>to_address</strong></td>
  <td>string</td>
  <td>hex-str(violas address)</td>
  <td>Payee Address</td>
 </tr>
 <tr>
  <td><strong><a href="#States---type">state</a></strong></td>
  <td>string</td>
  <td>start</td>
  <td>Mapping</td>
 </tr>
 <tr>
  <td><strong>times</strong></td>
  <td>uint64</td>
  <td>0~max(uint64)</td>
  <td>exchange execute times: 1</td>
 </tr>
</table>

```
'{"flag":"violas", "type":"v2em", "times": 1, "to_address":"0x89fF4a850e39A132614dbE517F80603b4A96fa0A", "state":"start"}'
```


### v2em - end

**Description**

ethereum erc20 token mapping violas mapping-token end


#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Flags---type">flag</a></strong></td>
  <td>string</td>
  <td>violas</td>
  <td>Differentiate transactions on different chains</td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>string</td>
  <td>v2em</td>
  <td>Distinguish between different mapping types</td>
 </tr>
 <tr>
  <td><strong>tran_id</strong></td>
  <td>string</td>
  <td>hex-str</td>
  <td>The tran_id corresponding to the transaction to be modified</td>
 </tr>
 <tr>
  <td><strong><a href="#States---type">state</a></strong></td>
  <td>string</td>
  <td>end</td>
  <td>Mapping completed</td>
 </tr>
</table>

```
'{"flag":"violas", "type":"v2em", "tran_id":"253896506a16795e895cb19429b569a2ca56ff5f37cb637032acd78c8a6fb588", "state":"end"}'
```

### funds

**Description**




#### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong><a href="#Flags---type">flag</a></strong></td>
  <td>string</td>
  <td>violas</td>
  <td>Differentiate transactions on different chains</td>
 </tr>
 <tr>
  <td><strong><a href="#Types---type">type</a></strong></td>
  <td>string</td>
  <td>funds</td>
  <td>Distinguish between different mapping types</td>
 </tr>
 <tr>
  <td><strong><a href="#Flags---type">flag</a></strong></td>
  <td>string</td>
  <td>btc/ethereum/violas/libra</td>
  <td>chain name</td>
 </tr>
 <tr>
  <td><strong>tran_id</strong></td>
  <td>string</td>
  <td>id</td>
  <td>id for transaction</td>
 </tr>
 <tr>
  <td><strong>token_id</strong></td>
  <td>string</td>
  <td>btc. etc</td>
  <td>get token id</td>
 </tr>
 <tr>
  <td><strong>amount</strong></td>
  <td>string</td>
  <td>int</td>
  <td>amount for transaction</td>
 </tr>
 <tr>
  <td><strong>to_address</strong></td>
  <td>string</td>
  <td>hex-str(violas address)</td>
  <td>Payee Address</td>
 </tr>
 <tr>
  <td><strong><a href="#States---type">state</a></strong></td>
  <td>string</td>
  <td>start</td>
  <td>Mapping</td>
 </tr>
</table>

```
'{"flag":"violas", "type":"v2em", "times": 1, "to_address":"0x89fF4a850e39A132614dbE517F80603b4A96fa0A", "state":"start"}'
```


---




# state change authority
  - start : client
  - cancel : client
  - end : server
  - stop : server

# state change 
  - start -> end
  - start -> stop
  - start -> cancel -> stop(Unrealized)


# version list

## v2.0.0
  - added violas stable token and libra stable token swap
  - added violas stable token and btc swap
  - added libra stable token and btc swap
  - added violas token and btc map


