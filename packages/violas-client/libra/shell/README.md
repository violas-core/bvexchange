
## Violas_shell running process of the first transaction
### step 1: Install violas-client from the [home page](https://github.com/palliums-developers/libra-client/tree/violas)

### step 2: Create a run script and copy it to the environment variable directory
Create violas_shell in the /usr/local/bin/ directory, and write the following code to violas_shell, set permissions to run (chmod +x violas_shell)
```python
#!/usr/bin/python3

# -*- coding: utf-8 -*-
import re
import sys

from libra.shell.libra_shell import main

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(main())                        
```
Run "violas_shell --help" , if it is as follows, the installation is successful
```text
usage: violas-shell [-h] [-a HOST] [-p PORT] [-r] [-s VALIDATOR_SET_FILE]
                    [-n MNEMONIC_FILE] [-m FAUCET_ACCOUNT_FILE] [-v] [-V]

optional arguments:
  -h, --help            show this help message and exit
  -a HOST, --host HOST  Host address/name to connect to
  -p PORT, --port PORT  Admission Control port to connect to. [default: 8000]
  -r, --sync            If set, client will sync with validator during wallet
                        recovery.
  -s VALIDATOR_SET_FILE, --validator_set_file VALIDATOR_SET_FILE
                        File location from which to load config of trusted
                        validators.
  -n MNEMONIC_FILE, --mnemonic_file MNEMONIC_FILE
                        File location from which to load mnemonic word for
                        user account address/key generation.
  -m FAUCET_ACCOUNT_FILE, --faucet_account_file FAUCET_ACCOUNT_FILE
                        Path to the generated keypair for the faucet account.
  -v, --verbose         Verbose output.
  -V, --version         show program's version number and exit
```
### Step 3: Run violas_shell
Run "violas_shell -a <host> -p <port> -s <validator_set_file> -m <faucet_account_file>"

### Step 4: Create account
Create two accounts for transfer and exchange  
Alice: 4a7435c24d7a3b7bbc31eec8037c90e988325b0547cf2a6c39d074598c855239  
Bob: 85e689b38a72252029f99f24057d7b22d190df33562d33a7d705471fc8c6e169
```text
violas% account create
>> Creating/retrieving next account from wallet
Created/retrieved account #0 address 4a7435c24d7a3b7bbc31eec8037c90e988325b0547cf2a6c39d074598c855239
violas% account create
>> Creating/retrieving next account from wallet
Created/retrieved account #1 address 85e689b38a72252029f99f24057d7b22d190df33562d33a7d705471fc8c6e169
violas% account list
User account index: 0, address: 4a7435c24d7a3b7bbc31eec8037c90e988325b0547cf2a6c39d074598c855239, sequence number: 0, status:AccountStatus.Local
User account index: 1, address: 85e689b38a72252029f99f24057d7b22d190df33562d33a7d705471fc8c6e169, sequence number: 0, status:AccountStatus.Local
Faucet account address: 000000000000000000000000000000000000000000000000000000000a550c18, sequence_number: 0, status: AccountStatus.Local
```

### Step 5：Mint platform coins
Mint 100 platform coins for two accounts for the gas fee
```text
violas% account mint 0 100
>> Minting coins
Mint request submitted
violas% account mint 1 100
>> Minting coins
Mint request submitted
violas% 
violas% q b 0 
Balance is: 100.0
violas% q b 1 
Balance is: 100.0
```

### Step 6: Alice releases contract
```text
violas% v publish 0 
>> Publishing module
Publish request submitted
```

### Step 7: Alice and Blob initialization
If you want to use a stable currency, the account needs to be initialized first. Otherwise any operation on the stable currency will fail
```text
violas% v init 0 0 
>> Initing module
init request submitted
violas% v init 1 0 
>> Initing module
init request submitted

```

### Step 8: Mint 50 stable currency for Alice
```text
violas% v mint 0 50 0 
>> Minting coins
Mint request submitted
violas% v b 0 0 
Balance is: 50.0
```

### Step 9: Alice transfers Bob 10 stable coins
```text
violas% v t 0 1 10 0 
>> Transferring
Transaction submitted to validator
To query for transaction status, run: query txn_acc_seq 0 0             <fetch_events=true|false>
violas% v b 0 0 
Balance is: 40.0
violas% v b 1 0 
Balance is: 10.0

```

### Step 10： Alice sells 5 stable coins, worth 10 platform coins
```text
violas% v r 0 0 5 10 
>> Transferring
Transaction submitted to validator
To query for transaction status, run: query txn_acc_seq 0 0             <fetch_events=true|false>
violas% v b 0 0 
Balance is: 35.0
violas% q b 0 
Balance is: 100.0
```

### Step 11: Bob takes Alice's order
```text
violas% v pi 1 0 0 
>> Transferring
Transaction submitted to validator
To query for transaction status, run: query txn_acc_seq 1 0             <fetch_events=true|false>
violas% v b 0 0 
Balance is: 35.0
violas% q b 0 
Balance is: 110.0
violas% q b 1
Balance is: 90.0
violas% v b 1 0 
Balance is: 15.0
```

### step 12: Alice cancels the order after the order is placed
```text
violas% v r 0 0 5 10 
>> Transferring
Transaction submitted to validator
To query for transaction status, run: query txn_acc_seq 0 0             <fetch_events=true|false>
violas% v b 0 0 
Balance is: 30.0
violas% 
violas% v w 0 0 
>> Transferring
Transaction submitted to validator
To query for transaction status, run: query txn_acc_seq 0 0             <fetch_events=true|false>
violas% v b 0 0 
Balance is: 35.0

```