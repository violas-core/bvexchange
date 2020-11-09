ADDRESS = "0xCb9b6D30E26d17Ce94A30Dd225dC336fC4536FE8"
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
            "inputs": [],
            "name": "Pause",
            "type": "event"
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
                    "internalType": "address",
                    "name": "token",
                    "type": "address"
                    },
                {
                    "indexed": false,
                    "internalType": "uint256",
                    "name": "amount",
                    "type": "uint256"
                    }
                ],
            "name": "TransferProof",
            "type": "event"
            },
        {
                "anonymous": false,
                "inputs": [],
                "name": "Unpause",
                "type": "event"
                },
        {
                "inputs": [],
                "name": "contractVersion",
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
                "name": "deprecated",
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
                "inputs": [],
                "name": "pause",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
                },
        {
                "inputs": [],
                "name": "paused",
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
                "inputs": [],
                "name": "payee",
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
                "name": "proofAddress",
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
                        "internalType": "string",
                        "name": "name",
                        "type": "string"
                        }
                    ],
                "name": "removeToken",
                "outputs": [
                    {
                        "internalType": "bool",
                        "name": "",
                        "type": "bool"
                        }
                    ],
                "stateMutability": "payable",
                "type": "function"
                },
        {
                "inputs": [
                    {
                        "internalType": "address",
                        "name": "tokenAddr",
                        "type": "address"
                        }
                    ],
                "name": "removeToken",
                "outputs": [
                    {
                        "internalType": "bool",
                        "name": "",
                        "type": "bool"
                        }
                    ],
                "stateMutability": "payable",
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
                        "internalType": "string",
                        "name": "name",
                        "type": "string"
                        }
                    ],
                "name": "tokenAddress",
                "outputs": [
                    {
                        "internalType": "address",
                        "name": "tokenAddrr",
                        "type": "address"
                        }
                    ],
                "stateMutability": "view",
                "type": "function"
                },
        {
                "inputs": [],
                "name": "tokenMaxCount",
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
                        "name": "tokenAddr",
                        "type": "address"
                        }
                    ],
                "name": "tokenName",
                "outputs": [
                    {
                        "internalType": "string",
                        "name": "name",
                        "type": "string"
                        }
                    ],
                "stateMutability": "view",
                "type": "function"
                },
        {
                "inputs": [
                    {
                        "internalType": "address",
                        "name": "tokenAddrr",
                        "type": "address"
                        },
                    {
                        "internalType": "address",
                        "name": "recipient",
                        "type": "address"
                        },
                    {
                        "internalType": "uint256",
                        "name": "amount",
                        "type": "uint256"
                        }
                    ],
                "name": "transfer",
                "outputs": [
                    {
                        "internalType": "bool",
                        "name": "",
                        "type": "bool"
                        }
                    ],
                "stateMutability": "payable",
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
                        "name": "newPayee",
                        "type": "address"
                        }
                    ],
                "name": "transferPayeeship",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
                },
        {
                "inputs": [
                    {
                        "internalType": "address",
                        "name": "tokenAddr",
                        "type": "address"
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
                "stateMutability": "payable",
                "type": "function"
                },
        {
                "inputs": [],
                "name": "unpause",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
                },
        {
                "inputs": [
                    {
                        "internalType": "string",
                        "name": "name",
                        "type": "string"
                        },
                    {
                        "internalType": "address",
                        "name": "tokenAddr",
                        "type": "address"
                        }
                    ],
                "name": "updateToken",
                "outputs": [
                    {
                        "internalType": "bool",
                        "name": "",
                        "type": "bool"
                        }
                    ],
                "stateMutability": "payable",
                "type": "function"
                },
        {
                "inputs": [
                    {
                        "internalType": "address",
                        "name": "proofAddr",
                        "type": "address"
                        }
                    ],
                "name": "upgradProofDatasAddress",
                "outputs": [
                    {
                        "internalType": "bool",
                        "name": "",
                        "type": "bool"
                        }
                    ],
                "stateMutability": "payable",
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
                "name": "validTokenNames",
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
                "stateMutability": "payable",
                "type": "receive"
                }
        ]
        '''

BYTECODE =""
