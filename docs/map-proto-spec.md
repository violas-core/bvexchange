# CONTENT

**Note**: The Mapping Protocol Specification is under development and may be updated in the future.

## Overview

Mapping Protocol is based on the [JSON](https://www.json.org/json-en.html) formats.This Specification defines the mapping types, and provides usage examples.

##JSON 
JSON (JavaScript Object Notation) is a lightweight data-interchange format, It is easy for humans to read and write. It is easy for machines to parse and generate. Refer to the[JSON](https://www.json.org/json-en.html)



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
  <td>mapping complete</td>
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
  <td><strong><a href="#States---type">state</a></strong></td>
  <td>string</td>
  <td>Transaction request type</td>
 </tr>
</table>
