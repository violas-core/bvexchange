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
   <td>libra's stable coin ≋USD mapping to violas‘s stable coin LBRUSD.</td>
  </tr>
  <tr>
   <td><strong>l2vgbt</strong></td>
   <td>string</td>
   <td>libra's stable coin ≋GBT mapping to violas‘s stable coin LBRGBT.</td>
  </tr>
  <tr>
   <td><strong>l2veur</strong></td>
   <td>string</td>
   <td>libra's stable coin ≋EUR mapping to violas‘s stable coin LBREUR.</td>
  </tr>
  <tr>
   <td><strong>l2vjpy</strong></td>
   <td>string</td>
   <td>libra's stable coin ≋JPY mapping to violas‘s stable coin LBRJPY.</td>
  </tr>
  <tr>
   <td><strong>l2vsgd</strong></td>
   <td>string</td>
   <td>libra's stable coin ≋SGD mapping to violas‘s stable coin LBRSGD.</td>
  </tr>
  <tr>
   <td><strong>v2lusd</strong></td>
   <td>string</td>
   <td>liolas's stable coin LBRUSD mapping to libra‘s stable coin ≋USD.</td>
  </tr>
  <tr>
   <td><strong>v2lgbt</strong></td>
   <td>string</td>
   <td>liolas's stable coin LBRGBT mapping to libra‘s stable coin ≋GBT.</td>
  </tr>
  <tr>
   <td><strong>v2leur</strong></td>
   <td>string</td>
   <td>liolas's stable coin LBREUR mapping to libra‘s stable coin ≋EUR.</td>
  </tr>
  <tr>
   <td><strong>v2ljpy</strong></td>
   <td>string</td>
   <td>liolas's stable coin LBRJPY mapping to libra‘s stable coin ≋JPY.</td>
  </tr>
  <tr>
   <td><strong>v2lsgd</strong></td>
   <td>string</td>
   <td>liolas's stable coin LBRSGD mapping to libra‘s stable coin ≋SGD.</td>
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
</table>

```
'{"flag":"libra", "type":"l2vusd", "to_address":"0000000000000000000000000000000059352b2c39bec33a880ae1334bea8129", "state":"start"}'
```


### l2vusd - end

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
  <td>end</td>
  <td>Mapping completed</td>
 </tr>
</table>

```
'{"flag":"libra", "type":"l2vusd", "tran_id":"253896506a16795e895cb19429b569a2ca56ff5f37cb637032acd78c8a6fb588", "state":"end"}'
```


### l2vgbt - start

**Description**

≋GBT Mapping LBRGBT


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
  <td>l2vgbt</td>
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
</table>

```
'{"flag":"libra", "type":"l2vgbt", "to_address":"0000000000000000000000000000000059352b2c39bec33a880ae1334bea8129", "state":"start"}'
```


### l2vgbt - end

**Description**

≋GBT Mapping LBRGBT complete


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
  <td>l2vgbt</td>
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
  <td>end</td>
  <td>Mapping completed</td>
 </tr>
</table>

```
'{"flag":"libra", "type":"l2vgbt", "tran_id":"253896506a16795e895cb19429b569a2ca56ff5f37cb637032acd78c8a6fb588", "state":"end"}'
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
</table>

```
'{"flag":"libra", "type":"l2veur", "to_address":"0000000000000000000000000000000059352b2c39bec33a880ae1334bea8129", "state":"start"}'
```


### l2veur - end

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
  <td>end</td>
  <td>Mapping completed</td>
 </tr>
</table>

```
'{"flag":"libra", "type":"l2veur", "tran_id":"253896506a16795e895cb19429b569a2ca56ff5f37cb637032acd78c8a6fb588", "state":"end"}'
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
</table>

```
'{"flag":"libra", "type":"l2vjpy", "to_address":"0000000000000000000000000000000059352b2c39bec33a880ae1334bea8129", "state":"start"}'
```


### l2vjpy - end

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
  <td>end</td>
  <td>Mapping completed</td>
 </tr>
</table>

```
'{"flag":"libra", "type":"l2vjpy", "tran_id":"253896506a16795e895cb19429b569a2ca56ff5f37cb637032acd78c8a6fb588", "state":"end"}'
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
</table>

```
'{"flag":"libra", "type":"l2vsgd", "to_address":"0000000000000000000000000000000059352b2c39bec33a880ae1334bea8129", "state":"start"}'
```


### l2vsgd - end

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
  <td>end</td>
  <td>Mapping completed</td>
 </tr>
</table>

```
'{"flag":"libra", "type":"l2vsgd", "tran_id":"253896506a16795e895cb19429b569a2ca56ff5f37cb637032acd78c8a6fb588", "state":"end"}'
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
</table>

```
'{"flag":"violas", "type":"v2lusd", "to_address":"0000000000000000000000000000000059352b2c39bec33a880ae1334bea8129", "state":"start"}'
```


### v2lusd - end

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
  <td>end</td>
  <td>Mapping completed</td>
 </tr>
</table>

```
'{"flag":"violas", "type":"v2lusd", "tran_id":"253896506a16795e895cb19429b569a2ca56ff5f37cb637032acd78c8a6fb588", "state":"end"}'
```


### v2lgbt - start

**Description**

LBRGBT Mapping ≋GBT


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
  <td>v2lgbt</td>
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
</table>

```
'{"flag":"violas", "type":"v2lgbt", "to_address":"0000000000000000000000000000000059352b2c39bec33a880ae1334bea8129", "state":"start"}'
```


### v2lgbt - end

**Description**

LBRGBT Mapping ≋GBT completed


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
  <td>v2lgbt</td>
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
  <td>end</td>
  <td>Mapping completed</td>
 </tr>
</table>

```
'{"flag":"violas", "type":"v2lgbt", "tran_id":"253896506a16795e895cb19429b569a2ca56ff5f37cb637032acd78c8a6fb588", "state":"end"}'
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
</table>

```
'{"flag":"violas", "type":"v2leur", "to_address":"0000000000000000000000000000000059352b2c39bec33a880ae1334bea8129", "state":"start"}'
```


### v2leur - end

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
  <td>end</td>
  <td>Mapping completed</td>
 </tr>
</table>

```
'{"flag":"violas", "type":"v2leur", "tran_id":"253896506a16795e895cb19429b569a2ca56ff5f37cb637032acd78c8a6fb588", "state":"end"}'
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
</table>

```
'{"flag":"violas", "type":"v2ljpy", "to_address":"0000000000000000000000000000000059352b2c39bec33a880ae1334bea8129", "state":"start"}'
```


### v2ljpy - end

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
  <td>end</td>
  <td>Mapping completed</td>
 </tr>
</table>

```
'{"flag":"violas", "type":"v2ljpy", "tran_id":"253896506a16795e895cb19429b569a2ca56ff5f37cb637032acd78c8a6fb588", "state":"end"}'
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
</table>

```
'{"flag":"violas", "type":"v2lsgd", "to_address":"0000000000000000000000000000000059352b2c39bec33a880ae1334bea8129", "state":"start"}'
```


### v2lsgd - end

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
  <td>end</td>
  <td>Mapping completed</td>
 </tr>
</table>

```
'{"flag":"violas", "type":"v2lsgd", "tran_id":"253896506a16795e895cb19429b569a2ca56ff5f37cb637032acd78c8a6fb588", "state":"end"}'
```
