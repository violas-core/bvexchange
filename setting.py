'''

bvexchange config
'''

traceback_limit = 4

#db logging echo(False, True) default: False
db_echo=False

#v2b max replay exchange count(state = faild)
v2b_maxtimes = 99

#btc connect 
btc_conn = {'rpcuser':'btc', 
        'rpcpassword':'btc', 
        'rpcip':'127.0.0.1', 
        'rpcport':18332}

#violas node list, to connect one
violas_nodes=[
        #       {'name':'' , 'host':'51.140.241.96', "port":40001, 'validator':'consensus_peers.config.toml', 'faucet':'faucet_keys'},
        {'name':'84', 'host':'52.27.228.84', "port":40001, 'validator':'consensus_peers.config.toml', 'faucet':'faucet_keys'},
        {'name':'242', 'host':'13.68.141.242', "port":40001, 'validator':'consensus_peers.config.toml', 'faucet':'faucet_keys'},
        {'name':'50', 'host':'47.52.195.50', "port":40001, 'validator':'consensus_peers.config.toml', 'faucet':'faucet_keys'},
        {'name':'235', 'host':'18.220.66.235', "port":40001, 'validator':'consensus_peers.config.toml', 'faucet':'faucet_keys'},
        ]

#libra node list, to connect one
libra_nodes=[
 #       {'host':'51.140.241.96', 'port':40001, 'validator':'consensus_peers.config.toml', 'faucet':'faucet_keys'},
         {'host':'ac.testnet.libra.org', 'port':8000, 'validator':'libra_consensus_peers.config.toml', 'faucet':'libra_faucet_keys', 'name':'libra'},
         #{'host':'125.39.5.57', 'port':40001, 'validator':'libra_consensus_peers.config.toml','faucet':'libra_faucet_keys', 'name':'tianjin'},
         #{'host':'125.39.5.57', 'port':40001},
        ]

#vioals server list. violas provides query of historical transactions. to connect one 
violas_servers=[
        {'host':'52.27.228.84', "port":4000, 'user':'violas', 'password':'violas'},
        ]

#db info type(vfilter vfilter lfilter v2b  l2b v2l)
db_list=[
        #'db_transactions':{'host':'127.0.0.1', 'port':6378, 'db':'3', 'password':'123'},
        #{'host':'127.0.0.1', 'port':6378, 'db':'lfilter', 'password':'violas', 'step':300},
        #{'host':'127.0.0.1', 'port':6378, 'db':'vfilter', 'password':'violas', 'step':300},
        #{'host':'127.0.0.1', 'port':6378, 'db':'v2b', 'password':'violas', 'step':100},
        #{'host':'127.0.0.1', 'port':6378, 'db':'l2v', 'password':'violas', 'step':100},
        #{'host':'127.0.0.1', 'port':6378, 'db':'v2l', 'password':'violas', 'step':100},
        #remote
        {'host':'192.168.31.37', 'port':6378, 'db':'lfilter', 'password':'violas', 'step':300},
        {'host':'192.168.31.37', 'port':6378, 'db':'vfilter', 'password':'violas', 'step':300},
        {'host':'192.168.31.37', 'port':6378, 'db':'v2b', 'password':'violas', 'step':100},
        {'host':'192.168.31.37', 'port':6378, 'db':'l2v', 'password':'violas', 'step':100},
        {'host':'192.168.31.37', 'port':6378, 'db':'v2l', 'password':'violas', 'step':100},
        #{'host':'127.0.0.1', 'port':6378, 'db':'lfilter', 'password':'violas', 'step':100},
        #{'host':'127.0.0.1', 'port':6378, 'db':'vfilter', 'password':'violas', 'step':200},
        #{'host':'127.0.0.1', 'port':6378, 'db':'v2b', 'password':'violas', 'step':100},
        #{'host':'127.0.0.1', 'port':6378, 'db':'l2v', 'password':'violas', 'step':100},
        #{'host':'127.0.0.1', 'port':6378, 'db':'v2l', 'password':'violas', 'step':100},
        ]

address_list = {
        #recever violas/libra coin
        'receiver':[
            ##vbtc -> btc
            {'address':'fd0426fa9a3ba4fae760d0f614591c61bb53232a3b1138d5078efa11ef07c49c', 'type':'v2b', 'chain':'violas'},
            ##vlibra -> libra
            {'address':'fd0426fa9a3ba4fae760d0f614591c61bb53232a3b1138d5078efa11ef07c49c', 'type':'v2l', 'chain':'violas'},
            ##libra -> vlibra
            {'address':'29223f25fe4b74d75ca87527aed560b2826f5da9382e2fb83f9ab740ac40b8f7', 'type':'l2v', 'chain':'libra'},
            ##btc -> vbtc
            {'address':'2MxBZG7295wfsXaUj69quf8vucFzwG35UWh', 'type':'b2v', 'chain':'btc'},
            {'address':'2N2YasTUdLbXsafHHmyoKUYcRRicRPgUyNB', 'type':'b2v', 'chain':'btc'},
            ],
        #send coin from this address
        'sender':[ 
            ##vbtc coin
            {'address':'216286b5329fddb9ec92d7bd998e09cd91694ed4adae85640dc232c6cec5d253', 'type':'b2v', 'chain':'violas'},
            ##btc coin
            {'address':'2N2YasTUdLbXsafHHmyoKUYcRRicRPgUyNB', 'type':'v2b', 'chain':'btc'},
            {'address':'2N9gZbqRiLKAhYCBFu3PquZwmqCBEwu1ien', 'type':'v2b', 'chain':'btc'},
            {'address':'2MxBZG7295wfsXaUj69quf8vucFzwG35UWh', 'type':'v2b', 'chain':'btc'},
            ##libra coin
            {'address':'b166e5272bb7bdc6fc2419b3f22939a3f42d0a9b0ccb97244af5b58e24a6d79e', 'type':'v2l', 'chain':'libra'},
            ##vlibra coin
            {'address':'216286b5329fddb9ec92d7bd998e09cd91694ed4adae85640dc232c6cec5d253', 'type':'l2v', 'chain':'violas'},
            ],
        #module address for type(violas nodes's vbtc or vlibra ...), type must be unique
        'module':[
            #vbtc module
            #{'address':'af955c1d62a74a7543235dbb7fa46ed98948d2041dff67dfdb636a54e84f91fb', 'type':'v2b-old', 'chain':'violas'},
            {'address':'2236322cf1e35198302919c2c1b1e4bf5be07359c8995c6a13ec53c17579c768', 'type':'v2b', 'chain':'violas'},
            #vbtc module
            {'address':'2236322cf1e35198302919c2c1b1e4bf5be07359c8995c6a13ec53c17579c768', 'type':'b2v', 'chain':'violas'},
            #vlibra module
            {'address':'61b578c0ebaad3852ea5e023fb0f59af61de1a5faf02b1211af0424ee5bbc410', 'type':'v2l', 'chain':'violas'},
            {'address':'0000000000000000000000000000000000000000000000000000000000000000', 'type':'v2l', 'chain':'libra'},
            #vlibra module
            {'address':'0000000000000000000000000000000000000000000000000000000000000000', 'type':'l2v', 'chain':'libra'},
            {'address':'61b578c0ebaad3852ea5e023fb0f59af61de1a5faf02b1211af0424ee5bbc410', 'type':'l2v', 'chain':'violas'},
            ],
        #combine coins to 
        'combine':[
            #vbtc
            {'address':'0bd77c4687547a66337c71532188dc88c76c59da4d6960fc82d72a2b15b06449', 'type':'v2b', 'chain':'violas'},
            {'address':'', 'type':'v2l', 'chain':'violas'},
            #vlibra
            {'address':'8cd3e23af9408d730b08684252871c370c9cd53bae2602face990473f4b2f9f8', 'type':'l2v', 'chain':'libra'},
            {'address':'2N9gZbqRiLKAhYCBFu3PquZwmqCBEwu1ien', 'type':'b2v', 'chain':'btc'},
            ],
        }

looping_sleep={
        'v2b' : 1,          #violas token exchange btc thread loop time(s)
        'b2v' : 1,          #btc exchange violas token thread loop time(s)
        'v2l' : 1,
        'l2v' : 1,
        'vfilter' : 1,      #violas blockchain transactions filter
        'lfilter' : 1,
        'v2bproof' : 1,     #communication thread loop time
        'v2lproof' : 1,     #communication thread loop time
        'comm': 8,          #communication thread loop time
        }
