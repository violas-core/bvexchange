ADDRESS = "0x93b774a66a37a9FfEE6Bc39760B1693B90356AF8"
ABI = '''
        [
        {
            "inputs": [
                {
                    "internalType": "string",
                    "name": "contractName",
                    "type": "string"
                    },
                {
                    "internalType": "string",
                    "name": "contractSymbol",
                    "type": "string"
                    }
                ],
            "stateMutability": "nonpayable",
            "type": "constructor"
            },
        {
            "inputs": [
                {
                    "internalType": "uint256",
                    "name": "stateValue",
                    "type": "uint256"
                    }
                ],
            "name": "checkState",
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
                    "internalType": "string",
                    "name": "stateName",
                    "type": "string"
                    }
                ],
            "name": "checkState",
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
                        "internalType": "string",
                        "name": "fromState",
                        "type": "string"
                        },
                    {
                        "internalType": "string",
                        "name": "toState",
                        "type": "string"
                        }
                    ],
                "name": "checkStateChange",
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
                        "name": "fromState",
                        "type": "uint256"
                        },
                    {
                        "internalType": "uint256",
                        "name": "toState",
                        "type": "uint256"
                        }
                    ],
                "name": "checkStateChange",
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
                        "name": "stateValue",
                        "type": "uint256"
                        }
                    ],
                "name": "getStateName",
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
                        "name": "stateName",
                        "type": "string"
                        }
                    ],
                "name": "getStateValue",
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
                "name": "maxStateValue",
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
                }
        ]
        '''
BYTECODE = ""
