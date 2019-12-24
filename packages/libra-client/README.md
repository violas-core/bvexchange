# ViolasClient  [![Build Status](https://travis-ci.org/yuan-xy/libra-client.svg?branch=master)](https://travis-ci.org/yuan-xy/libra-client) [![MIT licensed](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)


ViolasClient is a collection of tools which allows you interact whith [Libra Network](http://libra.org) easily. It provides three ways to access Libra:

1. `libra_shell`, an interactive shell program. It is compatible with official Libra client. For beginners, it lets you get started directly to try your first transaction with libra without requiring time-consuming downloads and compiles the huge entire Libra project source code.
2. `python api`, a collection of apis for client access to libra. For Python programmers, you can call this client side api to interact with Libra Network with more control than by using `libra` command.


## Installation

python 3.6
```shell script
$ git clone -b violas https://github.com/palliums-developers/libra-client.git
$ sudo cp -rf libra-client/libra/ /usr/local/lib/python3.6/dist-packages
$ pip3 install -r libra-client/requirements.txt
```

python3.7
```shell script
$ git clone -b violas https://github.com/palliums-developers/libra-client.git
$ sudo cp -rf libra-client/libra/ /usr/local/lib/python3.7/
$ pip3 install -r libra-client/requirements.txt
```


## Client side Libra API for python programmer


### Wallet

You can create a wallet using `WalletLibrary` class. A wallet is like your masterkey and you can create almost infinitely many Libra accounts from it. Note that LibraClient's mnemonic scheme is compatible with that of [Libra's CLI](https://github.com/libra/libra/tree/master/client/src), so you can import mnemonic between the two libraries.

```python
import libra

# Create a new random wallet
wallet = libra.WalletLibrary.new()

```

### Account

An `Account` can be created by calling `new_account` function on a wallet, each Account has an integer index in wallet, start from zero. An `Account` contains its `address`, `public_key`, and `private_key`.

```python

from libra import WalletLibrary

wallet = WalletLibrary.new()
a1 = wallet.new_account()

```

### Client

A `Client` must be created in order to send protobuf message to a Libra node. You can create a client with the following code.

```python
from libra import Client

client2 = Client.new('125.39.5.57', 46454)  # Client connecting to a local node
```


#### Get Account State Blob of an Address
You can use the get_account_blob function on the client to query the blob of the account. This function returns the account status blob and the json of the latest ledger version. 
```python
from libra import Client
from libra import WalletLibrary
from libra.json_print import json_print

wallet = WalletLibrary.new()
a1 = wallet.new_account()
client = Client.new('125.39.5.57',46454)
client.mint_coins(a1.address, 100, True)
json_print(client.get_account_blob(a1.address).to_json())
```

output
```text
{
    "blob": {
        "account_resource": {
            "authentication_key": "f0f5d3e6695fb381557dc1fe908376d417bd5b4ce72d03272accb53446b0a884",
            "balance": 100,
            "delegated_key_rotation_capability": false,
            "delegated_withdrawal_capability": false,
            "received_events": {
                "count": 1,
                "key": "f248bb3ce63826779596147815b1d703bff73b8bed61ec59cbab9102dd1101c7"
            },
            "sent_events": {
                "count": 0,
                "key": "eaec0f25b0d9b73f850572df83a33d36153c6367d18a5b594e6afd3aa3b5da65"
            },
            "sequence_number": 0
        },
        "violas_resource": {}
    },
    "version": 197
}
```
If the account has not been created (no funds have been received), the blob will be None.
```python
from libra import Client
from libra import WalletLibrary
from libra.json_print import json_print

wallet = WalletLibrary.new()
a1 = wallet.new_account()
client = Client.new('125.39.5.57',46454)
json_print(client.get_account_blob(a1.address).to_json())
```
output
```json
{
    "blob": null,
    "version": 195
}
```


#### Get Account State of an Address
If the Account has been created, you can call `get_account_state` function which return a `AccountState` ; other wise, AccountError will be thrown.

```python
from libra import Client
from libra import WalletLibrary
from libra.json_print import json_print

wallet = WalletLibrary.new()
a1 = wallet.new_account()
client = Client.new('125.39.5.57',46454)
client.mint_coins(a1.address, 100, True)
json_print(client.get_account_state(a1.address).to_json())
```
output
```json
{
    "account_resource": {
        "authentication_key": "2fa2a8d37c765a3e7bceabbfcb4c1c853f119ec3ae9b1ea6295bc98316c4396a",
        "balance": 100,
        "delegated_key_rotation_capability": false,
        "delegated_withdrawal_capability": false,
        "received_events": {
            "count": 1,
            "key": "3ee56aac429f6a26e1a4647bf326d7fba068d81df24df7544f7887937fb58174"
        },
        "sent_events": {
            "count": 0,
            "key": "8e9c245e3a95fec89527f1f59944eed882ae295f77f4893e8a3fac29de450641"
        },
        "sequence_number": 0
    },
    "violas_resource": {}
}
```

#### Get Account Resource of an Address
If you want to get account balance / sequence / authentication_key etc from account state, you can calling `get_account_resource` function, which will deserialize the account resource from account state map.

```python
from libra import Client
from libra import WalletLibrary
from libra.json_print import json_print

wallet = WalletLibrary.new()
a1 = wallet.new_account()
client = Client.new('125.39.5.57',46454)
client.mint_coins(a1.address, 100, True)
json_print(client.get_account_resource(a1.address).to_json())
```
output
```json
{
    "authentication_key": "4d59e77f8a4c38d96fbb20044949a4180ec1c41240299563e200371756db7a27",
    "balance": 100,
    "delegated_key_rotation_capability": false,
    "delegated_withdrawal_capability": false,
    "received_events": {
        "count": 1,
        "key": "473d22b4c6f95f097c1f1d47097f5931ef1fcd76556bcf1d14297c71460bba8a"
    },
    "sent_events": {
        "count": 0,
        "key": "2887468a238ba14fc793b10931366a6e0f28eaf25552037966170dae03d03eb1"
    },
    "sequence_number": 0
}
```

#### Get Libra Balance of an Address
If you just want to get the libra balance of an address, simply call `get_balance` function.

```python
from libra import Client
from libra import WalletLibrary

wallet = WalletLibrary.new()
a1 = wallet.new_account()
client = Client.new('125.39.5.57',46454)
client.mint_coins(a1.address, 100, True)
print(client.get_balance(a1.address))
```
output
```text
100
```

#### Get Sequence Number of an Address

If you just want to get the sequence number of an address, simply call `get_sequence_number` function.

```python
from libra import Client
from libra import WalletLibrary

wallet = WalletLibrary.new()
a1 = wallet.new_account()
a2 = wallet.new_account()
client = Client.new('125.39.5.57',46454)
client.mint_coins(a1.address, 100, True)
print(client.get_sequence_number(a1.address))
client.transfer_coin(a1, a2.address, 10, is_blocking=True)
print(client.get_sequence_number(a1.address))
```
output
```text
0
1
```

### Mint  Libra Token

You can mint  libra with `mint_coins` function.

```python
from libra import Client
from libra import WalletLibrary

wallet = WalletLibrary.new()
a1 = wallet.new_account()
a2 = wallet.new_account()
client = Client.new('125.39.5.57',46454)
client.mint_coins(a1.address, 100, True)
print(client.get_balance(a1.address))
```
output
```text
100
```

### Creating a Transfer Transaction Script and Sending the Transaction

```python
from libra import Client
from libra import WalletLibrary

wallet = WalletLibrary.new()
a1 = wallet.new_account()
a2 = wallet.new_account()
client = Client.new('125.39.5.57',46454)
client.mint_coins(a1.address, 100, True)
client.transfer_coin(a1, a2.address, 20, is_blocking=True)
print("a1 balance = ", client.get_balance(a1.address))
print("a2 balance = ", client.get_balance(a2.address))
```

When is_blocking param is False, the call will return as the transaction is submit to the validator node. When is_blocking param is True, the call will not return until the tranfer is actually executed or transaction waiting timeout.


### Query Transactions

Get transaction by version:

```python
from libra import Client
from libra import WalletLibrary
from libra.json_print import json_print

wallet = WalletLibrary.new()
a1 = wallet.new_account()
a2 = wallet.new_account()
client = Client.new('125.39.5.57',46454)
json_print(client.get_transaction(1).to_json())
```
output
```json
{
    "events": [],
    "public_key": "3aa8f39425f365b83285b20bd216031f5022fb5c63abd7dff329fd7a3d3fdd34",
    "raw_txn": {
        "expiration_time": 1572835936,
        "gas_unit_price": 0,
        "max_gas_amount": 140000,
        "payload": {
            "args": [
                "f8b7cc9a047d872b2237445adaaa325a8a3629feb253cd0fc6b30d164808b863",
                100
            ],
            "code": "4c49425241564d0a010007014a000000060000000350000000060000000d56000000060000000e5c0000000600000005620000003300000004950000002000000008b50000000f000000000000010002000300010400020002040200030204020300063c53454c463e0c4c696272614163636f756e74094c69627261436f696e046d61696e0f6d696e745f746f5f616464726573730000000000000000000000000000000000000000000000000000000000000000000100020004000c000c0113010102"
        },
        "sender": "000000000000000000000000000000000000000000000000000000000a550c18",
        "sequence_number": 1,
        "type": {
            "amount": "f8b7cc9a047d872b2237445adaaa325a8a3629feb253cd0fc6b30d164808b863",
            "sender": "000000000000000000000000000000000000000000000000000000000a550c18",
            "type": "mint"
        }
    },
    "signature": "3a6c51a2823adbbe517540daf735e22a20679ab22897e1457eab6c5d2daaa10aa8f4e015c04992a62e5e275e2bb2e26264c9e767cf7f598cfa6851f4e8526b0a",
    "version": 1
}

```
above code get transaction no.1, the return type is a ViolasSignedTransaction.


To get a list of transactions, If the fetch_event flag is True, then the event for the transaction is obtained:

```python
from libra import Client
from libra import WalletLibrary
from libra.json_print import json_print

wallet = WalletLibrary.new()
a1 = wallet.new_account()
a2 = wallet.new_account()
client = Client.new('125.39.5.57',46454)
txs = client.get_transactions(1, 3)
for tx in txs:
    json_print(tx.to_json())
```
output
```text
{
    "events": [],
    "public_key": "3aa8f39425f365b83285b20bd216031f5022fb5c63abd7dff329fd7a3d3fdd34",
    "raw_txn": {
        "expiration_time": 1572835936,
        "gas_unit_price": 0,
        "max_gas_amount": 140000,
        "payload": {
            "args": [
                "f8b7cc9a047d872b2237445adaaa325a8a3629feb253cd0fc6b30d164808b863",
                100
            ],
            "code": "4c49425241564d0a010007014a000000060000000350000000060000000d56000000060000000e5c0000000600000005620000003300000004950000002000000008b50000000f000000000000010002000300010400020002040200030204020300063c53454c463e0c4c696272614163636f756e74094c69627261436f696e046d61696e0f6d696e745f746f5f616464726573730000000000000000000000000000000000000000000000000000000000000000000100020004000c000c0113010102"
        },
        "sender": "000000000000000000000000000000000000000000000000000000000a550c18",
        "sequence_number": 1,
        "type": {
            "amount": "f8b7cc9a047d872b2237445adaaa325a8a3629feb253cd0fc6b30d164808b863",
            "sender": "000000000000000000000000000000000000000000000000000000000a550c18",
            "type": "mint"
        }
    },
    "signature": "3a6c51a2823adbbe517540daf735e22a20679ab22897e1457eab6c5d2daaa10aa8f4e015c04992a62e5e275e2bb2e26264c9e767cf7f598cfa6851f4e8526b0a",
    "version": 1
}
{
    "events": [],
    "public_key": "3aa8f39425f365b83285b20bd216031f5022fb5c63abd7dff329fd7a3d3fdd34",
    "raw_txn": {
        "expiration_time": 1572835943,
        "gas_unit_price": 0,
        "max_gas_amount": 140000,
        "payload": {
            "args": [
                "6e986f79d15da5dec4fd219209db1556d8d9533599ceb15086dbfb94ab5e3bb6",
                100
            ],
            "code": "4c49425241564d0a010007014a000000060000000350000000060000000d56000000060000000e5c0000000600000005620000003300000004950000002000000008b50000000f000000000000010002000300010400020002040200030204020300063c53454c463e0c4c696272614163636f756e74094c69627261436f696e046d61696e0f6d696e745f746f5f616464726573730000000000000000000000000000000000000000000000000000000000000000000100020004000c000c0113010102"
        },
        "sender": "000000000000000000000000000000000000000000000000000000000a550c18",
        "sequence_number": 2,
        "type": {
            "amount": "6e986f79d15da5dec4fd219209db1556d8d9533599ceb15086dbfb94ab5e3bb6",
            "sender": "000000000000000000000000000000000000000000000000000000000a550c18",
            "type": "mint"
        }
    },
    "signature": "4221940307575626367aa27ecbd3fa9eb43060fd420597ac85002e50ba8e128daca7b9f81a2b1e3ad567344c67f4ccac13ac05e246e25d5094314b6972bc6c00",
    "version": 2
}
{
    "events": [],
    "public_key": "3aa8f39425f365b83285b20bd216031f5022fb5c63abd7dff329fd7a3d3fdd34",
    "raw_txn": {
        "expiration_time": 1572835944,
        "gas_unit_price": 0,
        "max_gas_amount": 140000,
        "payload": {
            "args": [
                "45efd1d05aabc96c8a6dbdcb0e59bb23d2d538cb8d5ebd5af68fdaf039bb8dbc",
                100
            ],
            "code": "4c49425241564d0a010007014a000000060000000350000000060000000d56000000060000000e5c0000000600000005620000003300000004950000002000000008b50000000f000000000000010002000300010400020002040200030204020300063c53454c463e0c4c696272614163636f756e74094c69627261436f696e046d61696e0f6d696e745f746f5f616464726573730000000000000000000000000000000000000000000000000000000000000000000100020004000c000c0113010102"
        },
        "sender": "000000000000000000000000000000000000000000000000000000000a550c18",
        "sequence_number": 3,
        "type": {
            "amount": "45efd1d05aabc96c8a6dbdcb0e59bb23d2d538cb8d5ebd5af68fdaf039bb8dbc",
            "sender": "000000000000000000000000000000000000000000000000000000000a550c18",
            "type": "mint"
        }
    },
    "signature": "0c97285416f79be62dd2720d934dc58e9f0dbfac87879422eb183dd429c2da298f64e2316ec163fe31298e95a5278d5cad42fa5e10105df28ecd1400aed4d501",
    "version": 3
}

```

Get transaction by account sequence_number,If the fetch_event flag is True, then the event for the transaction is obtained:
```python
from libra import Client
from libra import WalletLibrary
from libra.json_print import json_print

wallet = WalletLibrary.new()
a1 = wallet.new_account()
a2 = wallet.new_account()
client = Client.new('125.39.5.57',46454)
client.mint_coins(a1.address, 100, True)
client.transfer_coin(a1, a2.address, 10, is_blocking=True)
json_print(client.get_account_transaction(a1.address, 0, True).to_json())
```
output
```json
{
    "events": [
        {
            "event": {
                "amount": 10,
                "payee": "8de686eb23a8b3b98f8c3781d8934646c4d5099e55678a8ce8255b9cedca7917"
            },
            "key": "c321fe319692d1fa2d207916764ab7a9f4e9bf2fc756f1d97aa2134275318d29",
            "sequence_number": 0
        },
        {
            "event": {
                "amount": 10,
                "payee": "34e21ff1d3839031e49ead42895446df073e7ec9382eabd001bd7bc932915589"
            },
            "key": "4ab0dca767c1a694c378c8da8c9b84c86ae58c6b4cfbb19e6a5d170ea7379f74",
            "sequence_number": 0
        }
    ],
    "public_key": "bd57777c42ddda9f9dc754a1dcf15c82e7bb3ae48fdf199d0276ce6e36d0a680",
    "raw_txn": {
        "expiration_time": 1572850041,
        "gas_unit_price": 0,
        "max_gas_amount": 140000,
        "payload": {
            "args": [
                "8de686eb23a8b3b98f8c3781d8934646c4d5099e55678a8ce8255b9cedca7917",
                10
            ],
            "code": "4c49425241564d0a010007014a00000004000000034e000000060000000d54000000060000000e5a0000000600000005600000002900000004890000002000000008a90000000f00000000000001000200010300020002040200030204020300063c53454c463e0c4c696272614163636f756e74046d61696e0f7061795f66726f6d5f73656e6465720000000000000000000000000000000000000000000000000000000000000000000100020004000c000c0113010102"
        },
        "sender": "34e21ff1d3839031e49ead42895446df073e7ec9382eabd001bd7bc932915589",
        "sequence_number": 0,
        "type": {
            "amount": 10,
            "receiver": "8de686eb23a8b3b98f8c3781d8934646c4d5099e55678a8ce8255b9cedca7917",
            "sender": "34e21ff1d3839031e49ead42895446df073e7ec9382eabd001bd7bc932915589",
            "type": "peer_to_peer_transfer"
        }
    },
    "signature": "9f866c08107e411b410bfddb350289087c0a2a35c0605b772a96e9aa0b7df6f0a5287d67d1ea35da6c2cf7f20610796f6832f66e08d30d970b9aef04463b9f03",
    "version": 220
}
```
### Query Events
To get the latest  events send by an version:

```python
from libra import Client
from libra import WalletLibrary
from libra.json_print import json_print

wallet = WalletLibrary.new()
a1 = wallet.new_account()
a2 = wallet.new_account()
client = Client.new('125.39.5.57',46454)
client.mint_coins(a1.address, 100, True)
client.transfer_coin(a1, a2.address, 10, is_blocking=True)
version = client.get_latest_transaction_version()
events = client.get_tx_events(version)
for event in events:
    json_print(event.to_json())
```
output
```text
{
    "event": {
        "amount": 10,
        "payee": "3136946f715d3b81740d715abae3b1e17ee95bd9341d493a8c078b77532bcbf5"
    },
    "key": "08ca411e13072ecc529faf523c74e04eccf3809d37f56976d9407776f72a0171",
    "sequence_number": 0
}
{
    "event": {
        "amount": 10,
        "payee": "40b0d8a47c15483f3d54f1694c629a1c6e798828974041e32194825b3150cdcf"
    },
    "key": "4d377972a11bbfd5f90a0f9414c0a57e99f77936784a802788f7a12271f2acda",
    "sequence_number": 0
}
```

To get the latest  events received by an address:

```python
from libra import Client
from libra import WalletLibrary
from libra.json_print import json_print

wallet = WalletLibrary.new()
a1 = wallet.new_account()
a2 = wallet.new_account()
client = Client.new('125.39.5.57',46454)
client.mint_coins(a1.address, 100, True)
client.transfer_coin(a1, a2.address, 10, is_blocking=True)
version = client.get_latest_transaction_version()
events = client.get_account_events(a1.address, 0)
for event in events:
    json_print(event.to_json())
```
output
```text
{
    "event": {
        "amount": 10,
        "payee": "afa54dc7801ec003dd6684686d3c72fb61b94f20e1d4b0ece9a92ac8639f6dbc"
    },
    "key": "da7e2802d21855b0fcb58d5e56121be9cfc56ccb98244beb702403ecd1ebca82",
    "sequence_number": 0
}
{
    "event": {
        "amount": 10,
        "payee": "fd8ee285c2fc34952b10a4dd396f145834995296ece182328015285d190f9747"
    },
    "key": "412055a0fdeb2313cccc60c549410fa2059e1a9b13da4e74b51eefb0da4680c5",
    "sequence_number": 0
}
```

### Publish constract

```python
from libra import Client
from libra import WalletLibrary
from libra.json_print import json_print

wallet = WalletLibrary.new()
a1 = wallet.new_account()
a2 = wallet.new_account()
client = Client.new('125.39.5.57',46454)
client.mint_coins(a1.address, 100, True)
print("before...........")
json_print(client.get_account_state(a1.address).to_json())
client.violas_publish(a1, True)
print("after...........")
json_print(client.get_account_state(a1.address).to_json())
```
output
```text
before...........
{
    "account_resource": {
        "authentication_key": "80b6efc397ec959a073aa6bd21dec312b4306bae7b3c66d6fc1ad08b1004566d",
        "balance": 100,
        "delegated_key_rotation_capability": false,
        "delegated_withdrawal_capability": false,
        "received_events": {
            "count": 1,
            "key": "e0c01caf1aea1b724bde73b54091fa185de555c58be878b2ee2d58341657a23f"
        },
        "sent_events": {
            "count": 0,
            "key": "7b3f8056f4ef839357f6dfc78b2742dd8ac3d8ccb99b5345788d9ddc41c8deb5"
        },
        "sequence_number": 0
    },
    "violas_resource": {}
}
waiting
no events emitted
after...........
{
    "account_resource": {
        "authentication_key": "80b6efc397ec959a073aa6bd21dec312b4306bae7b3c66d6fc1ad08b1004566d",
        "balance": 100,
        "delegated_key_rotation_capability": false,
        "delegated_withdrawal_capability": false,
        "received_events": {
            "count": 1,
            "key": "e0c01caf1aea1b724bde73b54091fa185de555c58be878b2ee2d58341657a23f"
        },
        "sent_events": {
            "count": 0,
            "key": "7b3f8056f4ef839357f6dfc78b2742dd8ac3d8ccb99b5345788d9ddc41c8deb5"
        },
        "sequence_number": 1
    },
    "violas_resource": {
        "00c353303556f345cb1db352507520830598f8b4e9308610cc7a2c0015ace6c0b5": "4c49425241564d0a01000b016e0000000e000000027c000000190000000395000000330000000cc80000000f0000000dd7000000520000000e290100008300000005ac010000590100000405030000400000000945030000140000000a590300001e0000000b77030000050300000000010101020103010401050106000701000008010000090100000a0100000b0200031b010102000c00000d00000e00000f0100100200110300120400130500140100150200160600170000180700190803220901150203230a0102010705010704000107010001040200000002010701000102000200020402000201020105070100000201020000020002040701000002000202020002000104000200040204020200020107050109000001020200020607050109000900010203010403000301070400030204010301020303040207010003010507010003030405070100020307040701000402060701000202030402040607010002030404020407010003050202040701000607020003060407030007010002060702000203070404070300070100020607020002030902040202040407040006070200060702000644546f6b656e0c4c696272614163636f756e740448617368054576656e74075536345574696c0b416464726573735574696c0d4279746561727261795574696c054f776e6572015404496e666f054f726465720d416c6c696e6f6e654576656e74077075626c69736811726571756972655f7075626c69736865640d726571756972655f6f776e6572046d696e740f6d696e745f746f5f616464726573730576616c75650762616c616e6365076465706f7369740877697468647261770f7061795f66726f6d5f73656e6465720a6d616b655f6f726465720c63616e63656c5f6f726465720a74616b655f6f726465720b656d69745f6576656e74730f616c6c696e6f6e655f6576656e74730648616e646c6505746f6b656e0570726963650565747970650673656e64657208726563656976657206616d6f756e74106e65775f6576656e745f68616e646c650a656d69745f6576656e7480b6efc397ec959a073aa6bd21dec312b4306bae7b3c66d6fc1ad08b1004566d00000000000000000000000000000000000000000000000000000000000000000002000001020100020201010302020204020604011100021a01031c02031d00041e00041f03042003041c03042100041d00000101020a0018002d0d000b002e0101040600020b00070023040c00140001320001060000000000000000140101320101130e021402013202010600000000000000000b00060000000000000000060000000000000000130d010201000001030b002d0d000c002e01010d010c0122040a00066500000000000000290202000001030b002d0d000c002e00010d010c0122040a000666000000000000002902030000030405001301011302010c0014010102040102010205050c000b011303010d020b000c021307010601000000000000000b000b01060000000000000000130d0102050000010604000c00110016020600010102070c001301012d0d000c003001010d010c011100160d020c020207000101030816001301012d0d020b002f01010d040b041100160d050c011501010d060b060d030c050c06180c04100017020800010103091a001301012d0d010c012f01010d020b021100160d030b030b002822041100066700000000000000290c030b00190c021000170c00140101020901020102060a0f001301012d0d020b011308010d030b000c031307010602000000000000000b000b01060000000000000000130d01020a01020102070b10001301012d0d020b001308010d030c030b011403013203010603000000000000000b020b000b01130d01020b0103010302060c16001301012d0d000b003103010d010c011503010d030d020f021305010d050b000c021307010604000000000000000b000b050b03130d01020c0103010302070d19001301012d0d010b003103010d020c021503010d040d030f031305010d060b000b04130f010b010c031307010605000000000000000b000b060b04130d01020d000102060e37002d0d0407000d050b000b040b010b050c020c031404010d06090415000b042f02010d070c0710010b061310020b00060100000000000000230420000b012f02010d080c0810010b061310020b0006020000000000000023042b000b012f02010d080c0810010b061310020b00060500000000000000230436000b012f02010d080c0810010b0613100202"
    }
}
```
Violas_resource adds a key, this key points to the module

### Init constract
```python
from libra import Client
from libra import WalletLibrary
from libra.json_print import json_print

wallet = WalletLibrary.new()
a1 = wallet.new_account()
a2 = wallet.new_account()
client = Client.new('125.39.5.57',46454)
client.mint_coins(a1.address, 100, True)
client.violas_publish(a1, True)
print("before...........")
json_print(client.get_account_state(a1.address).to_json())
client.violas_init(a1, a1.address, True)
print("after...........")
json_print(client.get_account_state(a1.address).to_json())
```
output
```text
{
    "account_resource": {
        "authentication_key": "dfec86c574647ea25f100d886a7b980f02db207436c0850d79368e8537d6465f",
        "balance": 100,
        "delegated_key_rotation_capability": false,
        "delegated_withdrawal_capability": false,
        "received_events": {
            "count": 1,
            "key": "ba834c828ae9b7e0ca16bf9a924edb269178efa8346488486b9bbcde6a61ea07"
        },
        "sent_events": {
            "count": 0,
            "key": "62cbc3b16f24fbb75aec0a50495f31787805571b99a1e075e5bd17c12419f498"
        },
        "sequence_number": 1
    },
    "violas_resource": {
        "00906e5b63f1fa040fb7787790429ac88b545705eb5969a24f51023d1fee359f06": "4c49425241564d0a01000b016e0000000e000000027c000000190000000395000000330000000cc80000000f0000000dd7000000520000000e290100008300000005ac010000590100000405030000400000000945030000140000000a590300001e0000000b77030000050300000000010101020103010401050106000701000008010000090100000a0100000b0200031b010102000c00000d00000e00000f0100100200110300120400130500140100150200160600170000180700190803220901150203230a0102010705010704000107010001040200000002010701000102000200020402000201020105070100000201020000020002040701000002000202020002000104000200040204020200020107050109000001020200020607050109000900010203010403000301070400030204010301020303040207010003010507010003030405070100020307040701000402060701000202030402040607010002030404020407010003050202040701000607020003060407030007010002060702000203070404070300070100020607020002030902040202040407040006070200060702000644546f6b656e0c4c696272614163636f756e740448617368054576656e74075536345574696c0b416464726573735574696c0d4279746561727261795574696c054f776e6572015404496e666f054f726465720d416c6c696e6f6e654576656e74077075626c69736811726571756972655f7075626c69736865640d726571756972655f6f776e6572046d696e740f6d696e745f746f5f616464726573730576616c75650762616c616e6365076465706f7369740877697468647261770f7061795f66726f6d5f73656e6465720a6d616b655f6f726465720c63616e63656c5f6f726465720a74616b655f6f726465720b656d69745f6576656e74730f616c6c696e6f6e655f6576656e74730648616e646c6505746f6b656e0570726963650565747970650673656e64657208726563656976657206616d6f756e74106e65775f6576656e745f68616e646c650a656d69745f6576656e74dfec86c574647ea25f100d886a7b980f02db207436c0850d79368e8537d6465f00000000000000000000000000000000000000000000000000000000000000000002000001020100020201010302020204020604011100021a01031c02031d00041e00041f03042003041c03042100041d00000101020a0018002d0d000b002e0101040600020b00070023040c00140001320001060000000000000000140101320101130e021402013202010600000000000000000b00060000000000000000060000000000000000130d010201000001030b002d0d000c002e01010d010c0122040a00066500000000000000290202000001030b002d0d000c002e00010d010c0122040a000666000000000000002902030000030405001301011302010c0014010102040102010205050c000b011303010d020b000c021307010601000000000000000b000b01060000000000000000130d0102050000010604000c00110016020600010102070c001301012d0d000c003001010d010c011100160d020c020207000101030816001301012d0d020b002f01010d040b041100160d050c011501010d060b060d030c050c06180c04100017020800010103091a001301012d0d010c012f01010d020b021100160d030b030b002822041100066700000000000000290c030b00190c021000170c00140101020901020102060a0f001301012d0d020b011308010d030b000c031307010602000000000000000b000b01060000000000000000130d01020a01020102070b10001301012d0d020b001308010d030c030b011403013203010603000000000000000b020b000b01130d01020b0103010302060c16001301012d0d000b003103010d010c011503010d030d020f021305010d050b000c021307010604000000000000000b000b050b03130d01020c0103010302070d19001301012d0d010b003103010d020c021503010d040d030f031305010d060b000b04130f010b010c031307010605000000000000000b000b060b04130d01020d000102060e37002d0d0407000d050b000b040b010b050c020c031404010d06090415000b042f02010d070c0710010b061310020b00060100000000000000230420000b012f02010d080c0810010b061310020b0006020000000000000023042b000b012f02010d080c0810010b061310020b00060500000000000000230436000b012f02010d080c0810010b0613100202"
    }
}
waiting
transaction is stored!
after...........
{
    "account_resource": {
        "authentication_key": "dfec86c574647ea25f100d886a7b980f02db207436c0850d79368e8537d6465f",
        "balance": 100,
        "delegated_key_rotation_capability": false,
        "delegated_withdrawal_capability": false,
        "received_events": {
            "count": 1,
            "key": "ba834c828ae9b7e0ca16bf9a924edb269178efa8346488486b9bbcde6a61ea07"
        },
        "sent_events": {
            "count": 0,
            "key": "62cbc3b16f24fbb75aec0a50495f31787805571b99a1e075e5bd17c12419f498"
        },
        "sequence_number": 2
    },
    "violas_resource": {
        "00906e5b63f1fa040fb7787790429ac88b545705eb5969a24f51023d1fee359f06": "4c49425241564d0a01000b016e0000000e000000027c000000190000000395000000330000000cc80000000f0000000dd7000000520000000e290100008300000005ac010000590100000405030000400000000945030000140000000a590300001e0000000b77030000050300000000010101020103010401050106000701000008010000090100000a0100000b0200031b010102000c00000d00000e00000f0100100200110300120400130500140100150200160600170000180700190803220901150203230a0102010705010704000107010001040200000002010701000102000200020402000201020105070100000201020000020002040701000002000202020002000104000200040204020200020107050109000001020200020607050109000900010203010403000301070400030204010301020303040207010003010507010003030405070100020307040701000402060701000202030402040607010002030404020407010003050202040701000607020003060407030007010002060702000203070404070300070100020607020002030902040202040407040006070200060702000644546f6b656e0c4c696272614163636f756e740448617368054576656e74075536345574696c0b416464726573735574696c0d4279746561727261795574696c054f776e6572015404496e666f054f726465720d416c6c696e6f6e654576656e74077075626c69736811726571756972655f7075626c69736865640d726571756972655f6f776e6572046d696e740f6d696e745f746f5f616464726573730576616c75650762616c616e6365076465706f7369740877697468647261770f7061795f66726f6d5f73656e6465720a6d616b655f6f726465720c63616e63656c5f6f726465720a74616b655f6f726465720b656d69745f6576656e74730f616c6c696e6f6e655f6576656e74730648616e646c6505746f6b656e0570726963650565747970650673656e64657208726563656976657206616d6f756e74106e65775f6576656e745f68616e646c650a656d69745f6576656e74dfec86c574647ea25f100d886a7b980f02db207436c0850d79368e8537d6465f00000000000000000000000000000000000000000000000000000000000000000002000001020100020201010302020204020604011100021a01031c02031d00041e00041f03042003041c03042100041d00000101020a0018002d0d000b002e0101040600020b00070023040c00140001320001060000000000000000140101320101130e021402013202010600000000000000000b00060000000000000000060000000000000000130d010201000001030b002d0d000c002e01010d010c0122040a00066500000000000000290202000001030b002d0d000c002e00010d010c0122040a000666000000000000002902030000030405001301011302010c0014010102040102010205050c000b011303010d020b000c021307010601000000000000000b000b01060000000000000000130d0102050000010604000c00110016020600010102070c001301012d0d000c003001010d010c011100160d020c020207000101030816001301012d0d020b002f01010d040b041100160d050c011501010d060b060d030c050c06180c04100017020800010103091a001301012d0d010c012f01010d020b021100160d030b030b002822041100066700000000000000290c030b00190c021000170c00140101020901020102060a0f001301012d0d020b011308010d030b000c031307010602000000000000000b000b01060000000000000000130d01020a01020102070b10001301012d0d020b001308010d030c030b011403013203010603000000000000000b020b000b01130d01020b0103010302060c16001301012d0d000b003103010d010c011503010d030d020f021305010d050b000c021307010604000000000000000b000b050b03130d01020c0103010302070d19001301012d0d010b003103010d020c021503010d040d030f031305010d060b000b04130f010b010c031307010605000000000000000b000b060b04130d01020d000102060e37002d0d0407000d050b000b040b010b050c020c031404010d06090415000b042f02010d070c0710010b061310020b00060100000000000000230420000b012f02010d080c0810010b061310020b0006020000000000000023042b000b012f02010d080c0810010b061310020b00060500000000000000230436000b012f02010d080c0810010b0613100202",
        "014b3661e6a794a0c81db23123555b10efaa02c89ce595088c719f1af4c92af476": "",
        "01674deac5e7fca75f00ca92b1ba3697f5f01ef585011beea7b361150f4504638f": 1,
        "019fa38ee6b4fe871512888f73e816e05ccd612b36dc256b875b46b3727cc6997d": {
            "allinone_events": {
                "count": 1,
                "key": "083739644e0bac8db9b3679a4659a738d3dc87993c57b97e3e7dbc5b689e7fd2"
            }
        },
        "01c704db273a6dd6ce6280a16de231fabde671bdff671ae3c658084b53d876cea1": 0
    }
}
```

### Mint Violas Coin

```python
from libra import Client
from libra import WalletLibrary

wallet = WalletLibrary.new()
a1 = wallet.new_account()
a2 = wallet.new_account()
client = Client.new('125.39.5.57',46454)
client.mint_coins(a1.address, 100, True)
client.violas_publish(a1, True)
client.violas_init(a1, a1.address, True)
print("before:", client.violas_get_balance(a1.address, a1.address))
client.violas_mint_coin(a1.address, 100, a1, True)
print("after:", client.violas_get_balance(a1.address, a1.address))

```
output
```text
before: 0
after: 100
```

### Transfer Violas Coin
```python
from libra import Client
from libra import WalletLibrary

wallet = WalletLibrary.new()
a1 = wallet.new_account()
a2 = wallet.new_account()
client = Client.new('125.39.5.57',46454)
client.mint_coins(a1.address, 100, True)
client.mint_coins(a2.address, 100, True)

client.violas_publish(a1, True)
client.violas_init(a1, a1.address, True)
client.violas_init(a2, a1.address, True)
client.violas_mint_coin(a1.address, 100, a1, True)
print("before:", client.violas_get_balance(a1.address, a1.address), client.violas_get_balance(a2.address, a1.address))
client.violas_transfer_coin(a1, a2.address, 20, a1.address, is_blocking=True)
print("after:", client.violas_get_balance(a1.address, a1.address), client.violas_get_balance(a2.address, a1.address))
```
output
```text
before: 100 0
after: 80 20
```

### Submit an exchange order
```python
from libra import Client
from libra import WalletLibrary

wallet = WalletLibrary.new()
a1 = wallet.new_account()
a2 = wallet.new_account()
client = Client.new('125.39.5.57',46454)
client.mint_coins(a1.address, 100, True)
client.mint_coins(a2.address, 100, True)

client.violas_publish(a1, True)
client.violas_init(a1, a1.address, True)
client.violas_init(a2, a1.address, True)
client.violas_mint_coin(a1.address, 100, a1, True)
print("before:", client.violas_get_balance(a1.address, a1.address))
client.violas_make_order(a1, a1.address, 20, 10, is_blocking=True)
print("after:", client.violas_get_balance(a1.address, a1.address))
```
output
```text
before: 100
after: 80
```
Submit an order to exchange 10 Libra coins with 20 violas

### Pick an exchange order
```python
from libra import Client
from libra import WalletLibrary
from libra.json_print import json_print

wallet = WalletLibrary.new()
a1 = wallet.new_account()
a2 = wallet.new_account()
client = Client.new('125.39.5.57',46454)
client.mint_coins(a1.address, 100, True)
client.mint_coins(a2.address, 100, True)

client.violas_publish(a1, True)
client.violas_init(a1, a1.address, True)
client.violas_init(a2, a1.address, True)
client.violas_mint_coin(a1.address, 100, a1, True)
print("before............")
print("libra balance:", "a1=", client.get_balance(a1.address), "a2=", client.get_balance(a2.address))
print("violas balance:", "a1=", client.violas_get_balance(a1.address, a1.address), "a2=", client.violas_get_balance(a2.address, a1.address))

client.violas_make_order(a1, a1.address, 20, 10, is_blocking=True)
client.violas_pick_order(a2, a1.address, a1.address, is_blocking=True)
print("after............")
print("libra balance:", "a1=", client.get_balance(a1.address), "a2=", client.get_balance(a2.address))
print("violas balance:", "a1=", client.violas_get_balance(a1.address, a1.address), "a2=", client.violas_get_balance(a2.address, a1.address))

```
output
```text
before............
libra balance: a1= 100 a2= 100
violas balance: a1= 100 a2= 0
after............
libra balance: a1= 110 a2= 90
violas balance: a1= 80 a2= 20
```

### Withdraw an exchange order
```python
from libra import Client
from libra import WalletLibrary

wallet = WalletLibrary.new()
a1 = wallet.new_account()
a2 = wallet.new_account()
client = Client.new('125.39.5.57',46454)
client.mint_coins(a1.address, 100, True)
client.mint_coins(a2.address, 100, True)

client.violas_publish(a1, True)
client.violas_init(a1, a1.address, True)
client.violas_init(a2, a1.address, True)
client.violas_mint_coin(a1.address, 100, a1, True)

client.violas_make_order(a1, a1.address, 20, 10, is_blocking=True)
print("before withdraw............")
print("violas balance:", client.violas_get_balance(a1.address, a1.address))
client.violas_withdraw_order(a1, a1.address, is_blocking=True)
print("after withdraw............")
print("violas balance:", client.violas_get_balance(a1.address, a1.address))
```

output
```text
before withdraw............
violas balance: 80
after withdraw............
violas balance: 100
```

### Withdraw an exchange order

```python
from libra import Client
from libra import WalletLibrary
from libra.json_print import json_print

wallet = WalletLibrary.new()
a1 = wallet.new_account()
a2 = wallet.new_account()
client = Client.new('125.39.5.57',46454)
client.mint_coins(a1.address, 100, True)
client.mint_coins(a2.address, 100, True)

client.violas_publish(a1, True)
client.violas_init(a1, a1.address, True)
client.violas_init(a2, a1.address, True)
client.violas_mint_coin(a1.address, 100, a1, True)

client.violas_make_order(a1, a1.address, 20, 10, is_blocking=True)
client.violas_withdraw_order(a1, a1.address, is_blocking=True)

json_print(client.get_account_transaction_type(a1.address, 0).to_json())
json_print(client.get_account_transaction_type(a1.address, 1).to_json())
json_print(client.get_account_transaction_type(a1.address, 2).to_json())
```

output
```text
{
    "sender": "3746ca50b2c13971332051577cd4b7b3aca0e40eb846eb6e0a1fb947a8d35aa7",
    "type": "violas_module"
}
{
    "module_address": "3746ca50b2c13971332051577cd4b7b3aca0e40eb846eb6e0a1fb947a8d35aa7",
    "sender": "3746ca50b2c13971332051577cd4b7b3aca0e40eb846eb6e0a1fb947a8d35aa7",
    "type": "violas_init"
}
{
    "amount": 100,
    "module_address": "3746ca50b2c13971332051577cd4b7b3aca0e40eb846eb6e0a1fb947a8d35aa7",
    "receiver": "3746ca50b2c13971332051577cd4b7b3aca0e40eb846eb6e0a1fb947a8d35aa7",
    "sender": "3746ca50b2c13971332051577cd4b7b3aca0e40eb846eb6e0a1fb947a8d35aa7",
    "type": "violas_mint"
}
```

## VStable to VStable
Submit exchange
```text
{
	"type": "sub_ex", 
	"addr": <address>,
	"amount": <amount>,
	"fee": <amount>,
	"exp": <time>
}
```
Feedback exchange
```text
{
	"type": "fb_ex",
	"ver": <version>,
	"fee": <amount>,
	"state": <state> #1: feedback of withdraw  2: feedback of expiration
}
```

Withdraw exchange
```text
{
	"type": "wd_ex",
	"ver": <version>
}
```
