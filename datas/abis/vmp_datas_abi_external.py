ADDRESS = "0x512364155BD156170f5484B863baf82108F5298b"
BYTECODE = ""
ABI = '''
        [
        {
            "inputs": [
                {
                    "internalType": "string",
                    "name": "_name",
                    "type": "string"
                    },
                {
                    "internalType": "string",
                    "name": "_symbol",
                    "type": "string"
                    }
                ],
            "stateMutability": "nonpayable",
            "type": "constructor"
            },
        {
            "anonymous": false,
            "inputs": [
                {
                    "indexed": true,
                    "internalType": "address",
                    "name": "from",
                    "type": "address"
                    },
                {
                    "indexed": true,
                    "internalType": "address",
                    "name": "to",
                    "type": "address"
                    },
                {
                    "indexed": false,
                    "internalType": "string",
                    "name": "datas",
                    "type": "string"
                    },
                {
                    "indexed": false,
                    "internalType": "address",
                    "name": "token",
                    "type": "address"
                    },
                {
                    "indexed": false,
                    "internalType": "uint256",
                    "name": "amount",
                    "type": "uint256"
                    },
                {
                    "indexed": false,
                    "internalType": "uint256",
                    "name": "state",
                    "type": "uint256"
                    }
                ],
            "name": "TransferProof",
            "type": "event"
            },
        {
                "anonymous": false,
                "inputs": [
                    {
                        "indexed": true,
                        "internalType": "address",
                        "name": "manager",
                        "type": "address"
                        },
                    {
                        "indexed": false,
                        "internalType": "uint256",
                        "name": "version",
                        "type": "uint256"
                        },
                    {
                        "indexed": false,
                        "internalType": "uint256",
                        "name": "state",
                        "type": "uint256"
                        }
                    ],
                "name": "TransferProofState",
                "type": "event"
                },
        {
                "inputs": [
                    {
                        "internalType": "address",
                        "name": "account",
                        "type": "address"
                        }
                    ],
                "name": "accountLatestVersion",
                "outputs": [
                    {
                        "internalType": "uint256",
                        "name": "",
                        "type": "uint256"
                        }
                    ],
                "stateMutability": "view",
                "type": "function"
                },
        {
                "inputs": [
                    {
                        "internalType": "address",
                        "name": "account",
                        "type": "address"
                        }
                    ],
                "name": "accountSequence",
                "outputs": [
                    {
                        "internalType": "uint256",
                        "name": "",
                        "type": "uint256"
                        }
                    ],
                "stateMutability": "view",
                "type": "function"
                },
        {
                "inputs": [
                    {
                        "internalType": "address",
                        "name": "account",
                        "type": "address"
                        },
                    {
                        "internalType": "uint256",
                        "name": "sequence",
                        "type": "uint256"
                        }
                    ],
                "name": "accountVersion",
                "outputs": [
                    {
                        "internalType": "uint256",
                        "name": "",
                        "type": "uint256"
                        }
                    ],
                "stateMutability": "view",
                "type": "function"
                },
        {
                "inputs": [
                    {
                        "internalType": "uint256",
                        "name": "version",
                        "type": "uint256"
                        }
                    ],
                "name": "addressIndex",
                "outputs": [
                    {
                        "internalType": "uint256",
                        "name": "sequence",
                        "type": "uint256"
                        },
                    {
                        "internalType": "address",
                        "name": "sender",
                        "type": "address"
                        },
                    {
                        "internalType": "bool",
                        "name": "create",
                        "type": "bool"
                        }
                    ],
                "stateMutability": "view",
                "type": "function"
                },
        {
                "inputs": [
                    {
                        "internalType": "address",
                        "name": "sender",
                        "type": "address"
                        }
                    ],
                "name": "addressProof",
                "outputs": [
                    {
                        "internalType": "uint256",
                        "name": "maxSequence",
                        "type": "uint256"
                        },
                    {
                        "internalType": "uint256",
                        "name": "minVersion",
                        "type": "uint256"
                        },
                    {
                        "internalType": "uint256",
                        "name": "maxVersion",
                        "type": "uint256"
                        },
                    {
                        "internalType": "bool",
                        "name": "inited",
                        "type": "bool"
                        }
                    ],
                "stateMutability": "view",
                "type": "function"
                },
        {
                "inputs": [],
                "name": "continuousComplete",
                "outputs": [
                    {
                        "internalType": "uint256",
                        "name": "",
                        "type": "uint256"
                        }
                    ],
                "stateMutability": "view",
                "type": "function"
                },
        {
                "inputs": [
                    {
                        "internalType": "address",
                        "name": "newManager",
                        "type": "address"
                        }
                    ],
                "name": "grantedMngPermission",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
                },
        {
                "inputs": [],
                "name": "mainAddress",
                "outputs": [
                    {
                        "internalType": "address",
                        "name": "",
                        "type": "address"
                        }
                    ],
                "stateMutability": "view",
                "type": "function"
                },
        {
                "inputs": [
                    {
                        "internalType": "address",
                        "name": "managerAddr",
                        "type": "address"
                        }
                    ],
                "name": "manageRoleState",
                "outputs": [
                    {
                        "internalType": "bool",
                        "name": "",
                        "type": "bool"
                        }
                    ],
                "stateMutability": "view",
                "type": "function"
                },
        {
                "inputs": [
                    {
                        "internalType": "uint256",
                        "name": "",
                        "type": "uint256"
                        }
                    ],
                "name": "manager",
                "outputs": [
                    {
                        "internalType": "address",
                        "name": "",
                        "type": "address"
                        }
                    ],
                "stateMutability": "view",
                "type": "function"
                },
        {
                "inputs": [],
                "name": "managerMaxCount",
                "outputs": [
                    {
                        "internalType": "uint256",
                        "name": "",
                        "type": "uint256"
                        }
                    ],
                "stateMutability": "view",
                "type": "function"
                },
        {
                "inputs": [],
                "name": "name",
                "outputs": [
                    {
                        "internalType": "string",
                        "name": "",
                        "type": "string"
                        }
                    ],
                "stateMutability": "view",
                "type": "function"
                },
        {
                "inputs": [],
                "name": "nextVersion",
                "outputs": [
                    {
                        "internalType": "uint256",
                        "name": "",
                        "type": "uint256"
                        }
                    ],
                "stateMutability": "view",
                "type": "function"
                },
        {
                "inputs": [],
                "name": "owner",
                "outputs": [
                    {
                        "internalType": "address",
                        "name": "",
                        "type": "address"
                        }
                    ],
                "stateMutability": "view",
                "type": "function"
                },
        {
                "inputs": [
                    {
                        "internalType": "uint256",
                        "name": "version",
                        "type": "uint256"
                        }
                    ],
                "name": "proofInfo",
                "outputs": [
                    {
                        "internalType": "string",
                        "name": "",
                        "type": "string"
                        },
                    {
                        "internalType": "uint256",
                        "name": "",
                        "type": "uint256"
                        },
                    {
                        "internalType": "uint256",
                        "name": "",
                        "type": "uint256"
                        },
                    {
                        "internalType": "address",
                        "name": "",
                        "type": "address"
                        },
                    {
                        "internalType": "address",
                        "name": "",
                        "type": "address"
                        },
                    {
                        "internalType": "uint256",
                        "name": "",
                        "type": "uint256"
                        },
                    {
                        "internalType": "bool",
                        "name": "",
                        "type": "bool"
                        }
                    ],
                "stateMutability": "view",
                "type": "function"
                },
        {
                "inputs": [
                    {
                        "internalType": "address",
                        "name": "sender",
                        "type": "address"
                        },
                    {
                        "internalType": "uint256",
                        "name": "sequence",
                        "type": "uint256"
                        }
                    ],
                "name": "proofInfo",
                "outputs": [
                    {
                        "internalType": "string",
                        "name": "",
                        "type": "string"
                        },
                    {
                        "internalType": "uint256",
                        "name": "",
                        "type": "uint256"
                        },
                    {
                        "internalType": "uint256",
                        "name": "",
                        "type": "uint256"
                        },
                    {
                        "internalType": "address",
                        "name": "",
                        "type": "address"
                        },
                    {
                        "internalType": "uint256",
                        "name": "",
                        "type": "uint256"
                        },
                    {
                        "internalType": "uint256",
                        "name": "",
                        "type": "uint256"
                        }
                    ],
                "stateMutability": "view",
                "type": "function"
                },
        {
                "inputs": [
                    {
                        "internalType": "address",
                        "name": "managerAddr",
                        "type": "address"
                        }
                    ],
                "name": "revokeMngPermission",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
                },
        {
                "inputs": [],
                "name": "stateAddress",
                "outputs": [
                    {
                        "internalType": "address",
                        "name": "",
                        "type": "address"
                        }
                    ],
                "stateMutability": "view",
                "type": "function"
                },
        {
                "inputs": [],
                "name": "symbol",
                "outputs": [
                    {
                        "internalType": "string",
                        "name": "",
                        "type": "string"
                        }
                    ],
                "stateMutability": "view",
                "type": "function"
                },
        {
                "inputs": [
                    {
                        "internalType": "uint256",
                        "name": "verion",
                        "type": "uint256"
                        }
                    ],
                "name": "transferContinuousComplete",
                "outputs": [
                    {
                        "internalType": "bool",
                        "name": "",
                        "type": "bool"
                        }
                    ],
                "stateMutability": "nonpayable",
                "type": "function"
                },
        {
                "inputs": [
                    {
                        "internalType": "address",
                        "name": "newOwner",
                        "type": "address"
                        }
                    ],
                "name": "transferOwnership",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
                },
        {
                "inputs": [
                    {
                        "internalType": "address",
                        "name": "fromAddr",
                        "type": "address"
                        },
                    {
                        "internalType": "address",
                        "name": "toAddr",
                        "type": "address"
                        },
                    {
                        "internalType": "address",
                        "name": "token",
                        "type": "address"
                        },
                    {
                        "internalType": "uint256",
                        "name": "amount",
                        "type": "uint256"
                        },
                    {
                        "internalType": "string",
                        "name": "datas",
                        "type": "string"
                        }
                    ],
                "name": "transferProof",
                "outputs": [
                    {
                        "internalType": "bool",
                        "name": "",
                        "type": "bool"
                        }
                    ],
                "stateMutability": "nonpayable",
                "type": "function"
                },
        {
                "inputs": [
                    {
                        "internalType": "address",
                        "name": "sender",
                        "type": "address"
                        },
                    {
                        "internalType": "uint256",
                        "name": "sequence",
                        "type": "uint256"
                        },
                    {
                        "internalType": "string",
                        "name": "state",
                        "type": "string"
                        }
                    ],
                "name": "transferProofState",
                "outputs": [
                    {
                        "internalType": "bool",
                        "name": "",
                        "type": "bool"
                        }
                    ],
                "stateMutability": "nonpayable",
                "type": "function"
                },
        {
                "inputs": [
                    {
                        "internalType": "uint256",
                        "name": "version",
                        "type": "uint256"
                        },
                    {
                        "internalType": "uint256",
                        "name": "state",
                        "type": "uint256"
                        }
                    ],
                "name": "transferProofState",
                "outputs": [
                    {
                        "internalType": "bool",
                        "name": "",
                        "type": "bool"
                        }
                    ],
                "stateMutability": "nonpayable",
                "type": "function"
                },
        {
                "inputs": [
                    {
                        "internalType": "address",
                        "name": "sender",
                        "type": "address"
                        },
                    {
                        "internalType": "uint256",
                        "name": "sequence",
                        "type": "uint256"
                        },
                    {
                        "internalType": "uint256",
                        "name": "state",
                        "type": "uint256"
                        }
                    ],
                "name": "transferProofState",
                "outputs": [
                    {
                        "internalType": "bool",
                        "name": "",
                        "type": "bool"
                        }
                    ],
                "stateMutability": "nonpayable",
                "type": "function"
                },
        {
                "inputs": [
                    {
                        "internalType": "uint256",
                        "name": "version",
                        "type": "uint256"
                        },
                    {
                        "internalType": "string",
                        "name": "state",
                        "type": "string"
                        }
                    ],
                "name": "transferProofState",
                "outputs": [
                    {
                        "internalType": "bool",
                        "name": "",
                        "type": "bool"
                        }
                    ],
                "stateMutability": "nonpayable",
                "type": "function"
                },
        {
                "inputs": [
                    {
                        "internalType": "address",
                        "name": "mainAddr",
                        "type": "address"
                        }
                    ],
                "name": "upgradMainAddress",
                "outputs": [
                    {
                        "internalType": "bool",
                        "name": "",
                        "type": "bool"
                        }
                    ],
                "stateMutability": "nonpayable",
                "type": "function"
                },
        {
                "inputs": [
                    {
                        "internalType": "address",
                        "name": "stateAddr",
                        "type": "address"
                        }
                    ],
                "name": "upgradStateAddress",
                "outputs": [
                    {
                        "internalType": "bool",
                        "name": "",
                        "type": "bool"
                        }
                    ],
                "stateMutability": "nonpayable",
                "type": "function"
                },
        {
                "stateMutability": "payable",
                "type": "receive"
                }
        ]
        '''

