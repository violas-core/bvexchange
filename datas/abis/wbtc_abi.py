BYTECODE = ""

ADDRESS = "0xB883664F0095DE55491927B6829fF9BF4ab4d8A1"
ABI = '''
        [
        {
            "constant": false,
            "inputs": [
                {
                    "name": "_spender",
                    "type": "address"
                    },
                {
                    "name": "_value",
                    "type": "uint256"
                    }
                ],
            "name": "approve",
            "outputs": [
                {
                    "name": "",
                    "type": "bool"
                    }
                ],
            "payable": false,
            "stateMutability": "nonpayable",
            "type": "function"
            },
        {
            "constant": false,
            "inputs": [
                {
                    "name": "value",
                    "type": "uint256"
                    }
                ],
            "name": "burn",
            "outputs": [],
            "payable": false,
            "stateMutability": "nonpayable",
            "type": "function"
            },
        {
            "constant": false,
            "inputs": [],
            "name": "claimOwnership",
            "outputs": [],
            "payable": false,
            "stateMutability": "nonpayable",
            "type": "function"
            },
        {
            "constant": false,
            "inputs": [
                {
                    "name": "_spender",
                    "type": "address"
                    },
                {
                    "name": "_subtractedValue",
                    "type": "uint256"
                    }
                ],
            "name": "decreaseApproval",
            "outputs": [
                {
                    "name": "success",
                    "type": "bool"
                    }
                ],
            "payable": false,
            "stateMutability": "nonpayable",
            "type": "function"
            },
        {
                "constant": false,
                "inputs": [],
                "name": "finishMinting",
                "outputs": [
                    {
                        "name": "",
                        "type": "bool"
                        }
                    ],
                "payable": false,
                "stateMutability": "nonpayable",
                "type": "function"
                },
        {
                "constant": false,
                "inputs": [
                    {
                        "name": "_spender",
                        "type": "address"
                        },
                    {
                        "name": "_addedValue",
                        "type": "uint256"
                        }
                    ],
                "name": "increaseApproval",
                "outputs": [
                    {
                        "name": "success",
                        "type": "bool"
                        }
                    ],
                "payable": false,
                "stateMutability": "nonpayable",
                "type": "function"
                },
        {
                "constant": false,
                "inputs": [
                    {
                        "name": "_to",
                        "type": "address"
                        },
                    {
                        "name": "_amount",
                        "type": "uint256"
                        }
                    ],
                "name": "mint",
                "outputs": [
                    {
                        "name": "",
                        "type": "bool"
                        }
                    ],
                "payable": false,
                "stateMutability": "nonpayable",
                "type": "function"
                },
        {
                "constant": false,
                "inputs": [],
                "name": "pause",
                "outputs": [],
                "payable": false,
                "stateMutability": "nonpayable",
                "type": "function"
                },
        {
                "constant": false,
                "inputs": [
                    {
                        "name": "_token",
                        "type": "address"
                        }
                    ],
                "name": "reclaimToken",
                "outputs": [],
                "payable": false,
                "stateMutability": "nonpayable",
                "type": "function"
                },
        {
                "constant": false,
                "inputs": [],
                "name": "renounceOwnership",
                "outputs": [],
                "payable": false,
                "stateMutability": "nonpayable",
                "type": "function"
                },
        {
                "constant": false,
                "inputs": [
                    {
                        "name": "_to",
                        "type": "address"
                        },
                    {
                        "name": "_value",
                        "type": "uint256"
                        }
                    ],
                "name": "transfer",
                "outputs": [
                    {
                        "name": "",
                        "type": "bool"
                        }
                    ],
                "payable": false,
                "stateMutability": "nonpayable",
                "type": "function"
                },
        {
                "constant": false,
                "inputs": [
                    {
                        "name": "_from",
                        "type": "address"
                        },
                    {
                        "name": "_to",
                        "type": "address"
                        },
                    {
                        "name": "_value",
                        "type": "uint256"
                        }
                    ],
                "name": "transferFrom",
                "outputs": [
                    {
                        "name": "",
                        "type": "bool"
                        }
                    ],
                "payable": false,
                "stateMutability": "nonpayable",
                "type": "function"
                },
        {
                "constant": false,
                "inputs": [
                    {
                        "name": "newOwner",
                        "type": "address"
                        }
                    ],
                "name": "transferOwnership",
                "outputs": [],
                "payable": false,
                "stateMutability": "nonpayable",
                "type": "function"
                },
        {
                "constant": false,
                "inputs": [],
                "name": "unpause",
                "outputs": [],
                "payable": false,
                "stateMutability": "nonpayable",
                "type": "function"
                },
        {
                "anonymous": false,
                "inputs": [],
                "name": "Pause",
                "type": "event"
                },
        {
                "anonymous": false,
                "inputs": [],
                "name": "Unpause",
                "type": "event"
                },
        {
                "anonymous": false,
                "inputs": [
                    {
                        "indexed": true,
                        "name": "burner",
                        "type": "address"
                        },
                    {
                        "indexed": false,
                        "name": "value",
                        "type": "uint256"
                        }
                    ],
                "name": "Burn",
                "type": "event"
                },
        {
                "anonymous": false,
                "inputs": [
                    {
                        "indexed": true,
                        "name": "to",
                        "type": "address"
                        },
                    {
                        "indexed": false,
                        "name": "amount",
                        "type": "uint256"
                        }
                    ],
                "name": "Mint",
                "type": "event"
                },
        {
                "anonymous": false,
                "inputs": [],
                "name": "MintFinished",
                "type": "event"
                },
        {
                "anonymous": false,
                "inputs": [
                    {
                        "indexed": true,
                        "name": "previousOwner",
                        "type": "address"
                        }
                    ],
                "name": "OwnershipRenounced",
                "type": "event"
                },
        {
                "anonymous": false,
                "inputs": [
                    {
                        "indexed": true,
                        "name": "previousOwner",
                        "type": "address"
                        },
                    {
                        "indexed": true,
                        "name": "newOwner",
                        "type": "address"
                        }
                    ],
                "name": "OwnershipTransferred",
                "type": "event"
                },
        {
                "anonymous": false,
                "inputs": [
                    {
                        "indexed": true,
                        "name": "owner",
                        "type": "address"
                        },
                    {
                        "indexed": true,
                        "name": "spender",
                        "type": "address"
                        },
                    {
                        "indexed": false,
                        "name": "value",
                        "type": "uint256"
                        }
                    ],
                "name": "Approval",
                "type": "event"
                },
        {
                "anonymous": false,
                "inputs": [
                    {
                        "indexed": true,
                        "name": "from",
                        "type": "address"
                        },
                    {
                        "indexed": true,
                        "name": "to",
                        "type": "address"
                        },
                    {
                        "indexed": false,
                        "name": "value",
                        "type": "uint256"
                        }
                    ],
                "name": "Transfer",
                "type": "event"
                },
        {
                "constant": true,
                "inputs": [
                    {
                        "name": "_owner",
                        "type": "address"
                        },
                    {
                        "name": "_spender",
                        "type": "address"
                        }
                    ],
                "name": "allowance",
                "outputs": [
                    {
                        "name": "",
                        "type": "uint256"
                        }
                    ],
                "payable": false,
                "stateMutability": "view",
                "type": "function"
                },
        {
                "constant": true,
                "inputs": [
                    {
                        "name": "_owner",
                        "type": "address"
                        }
                    ],
                "name": "balanceOf",
                "outputs": [
                    {
                        "name": "",
                        "type": "uint256"
                        }
                    ],
                "payable": false,
                "stateMutability": "view",
                "type": "function"
                },
        {
                "constant": true,
                "inputs": [],
                "name": "decimals",
                "outputs": [
                    {
                        "name": "",
                        "type": "uint8"
                        }
                    ],
                "payable": false,
                "stateMutability": "view",
                "type": "function"
                },
        {
                "constant": true,
                "inputs": [],
                "name": "mintingFinished",
                "outputs": [
                    {
                        "name": "",
                        "type": "bool"
                        }
                    ],
                "payable": false,
                "stateMutability": "view",
                "type": "function"
                },
        {
                "constant": true,
                "inputs": [],
                "name": "name",
                "outputs": [
                    {
                        "name": "",
                        "type": "string"
                        }
                    ],
                "payable": false,
                "stateMutability": "view",
                "type": "function"
                },
        {
                "constant": true,
                "inputs": [],
                "name": "owner",
                "outputs": [
                    {
                        "name": "",
                        "type": "address"
                        }
                    ],
                "payable": false,
                "stateMutability": "view",
                "type": "function"
                },
        {
                "constant": true,
                "inputs": [],
                "name": "paused",
                "outputs": [
                    {
                        "name": "",
                        "type": "bool"
                        }
                    ],
                "payable": false,
                "stateMutability": "view",
                "type": "function"
                },
        {
                "constant": true,
                "inputs": [],
                "name": "pendingOwner",
                "outputs": [
                    {
                        "name": "",
                        "type": "address"
                        }
                    ],
                "payable": false,
                "stateMutability": "view",
                "type": "function"
                },
        {
                "constant": true,
                "inputs": [],
                "name": "symbol",
                "outputs": [
                    {
                        "name": "",
                        "type": "string"
                        }
                    ],
                "payable": false,
                "stateMutability": "view",
                "type": "function"
                },
        {
                "constant": true,
                "inputs": [],
                "name": "totalSupply",
                "outputs": [
                    {
                        "name": "",
                        "type": "uint256"
                        }
                    ],
                "payable": false,
                "stateMutability": "view",
                "type": "function"
                }
        ]
        '''
