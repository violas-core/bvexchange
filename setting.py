'''

bvexchange config
'''

traceback_limit = 4

#db logging echo(False, True) default: False
db_echo=False

#v2b max replay exchange count(state = faild)
v2b_maxtimes = 99999

#btc connect 
btc_conn = {'rpcuser':'btc', 
        'rpcpassword':'btc', 
        'rpcip':'192.168.1.196', 
        'rpcport':18332}

#violas node list, to connect one
violas_nodes=[
 #       {'host':'51.140.241.96', "port":40001, 'validator':'consensus_peers.config.toml', 'faucet':'faucet_keys'},
        {'host':'13.68.141.242', "port":40001, 'validator':'consensus_peers.config.toml', 'faucet':'faucet_keys'},
        {'host':'47.52.195.50', "port":40001, 'validator':'consensus_peers.config.toml', 'faucet':'faucet_keys'},
        {'host':'18.220.66.235', "port":40001, 'validator':'consensus_peers.config.toml', 'faucet':'faucet_keys'},
        {'host':'52.27.228.84', "port":40001, 'validator':'consensus_peers.config.toml', 'faucet':'faucet_keys'},
        ]

#libra node list, to connect one
libra_nodes=[
 #       {'host':'51.140.241.96', 'port':40001, 'validator':'consensus_peers.config.toml', 'faucet':'faucet_keys'},
         {'host':'ac.testnet.libra.org', 'port':8000, 'validator':'libra_consensus_peers.config.toml', 'faucet':'libra_faucet_keys'}
         #{'host':'125.39.5.57', 'port':40001, 'validator':'libra_consensus_peers.config.toml','faucet':'libra_faucet_keys'},
         #{'host':'125.39.5.57', 'port':40001},
        ]

#vioals server list. violas provides query of historical transactions. to connect one 
violas_servers=[
        {'host':'52.27.228.84', "port":4000, 'user':'violas', 'password':'violas'},
        ]

#db info type(vfilter vfilter lfilter v2b  l2b v2l)
db_list=[
        #'db_transactions':{'host':'127.0.0.1', 'port':6378, 'db':'3', 'password':'123'},
        {'host':'127.0.0.1', 'port':6378, 'db':'lfilter', 'password':'violas', 'step':1000},
        {'host':'127.0.0.1', 'port':6378, 'db':'vfilter', 'password':'violas', 'step':1000},
        {'host':'127.0.0.1', 'port':6378, 'db':'v2b', 'password':'violas', 'step':100},
        {'host':'127.0.0.1', 'port':6378, 'db':'l2v', 'password':'violas', 'step':100},
        {'host':'127.0.0.1', 'port':6378, 'db':'v2l', 'password':'violas', 'step':100},
        ]

address_list = {
        #recever violas coin
        'receiver':[
            {'address':'1b3920fb9703cace285ac9ef5b54886b8b7a85442a8b38e06237908c3dfc1e5c', 'type':'v2b', 'chain':'violas'},
            {'address':'1b3920fb9703cace285ac9ef5b54886b8b7a85442a8b38e06237908c3dfc1e5c', 'type':'v2l', 'chain':'violas'},
            {'address':'1b3920fb9703cace285ac9ef5b54886b8b7a85442a8b38e06237908c3dfc1e5c', 'type':'l2v', 'chain':'libra'},
            {'address':'2MxBZG7295wfsXaUj69quf8vucFzwG35UWh', 'type':'b2v', 'chain':'btc'},
            {'address':'2N2YasTUdLbXsafHHmyoKUYcRRicRPgUyNB', 'type':'b2v', 'chain':'btc'},
            ],
        #send coin from this address
        'sender':[
            {'address':'210a283f13e42a37b7fb2dec50d8c2b28d6cc7e4f041fbdfa4998aa1b5663b89', 'type':'b2v', 'chain':'violas'},
            {'address':'2N2YasTUdLbXsafHHmyoKUYcRRicRPgUyNB', 'type':'v2b', 'chain':'btc'},
            {'address':'2N9gZbqRiLKAhYCBFu3PquZwmqCBEwu1ien', 'type':'v2b', 'chain':'btc'},
            {'address':'2MxBZG7295wfsXaUj69quf8vucFzwG35UWh', 'type':'v2b', 'chain':'btc'},
            {'address':'210a283f13e42a37b7fb2dec50d8c2b28d6cc7e4f041fbdfa4998aa1b5663b89', 'type':'v2l', 'chain':'violas'},
            {'address':'210a283f13e42a37b7fb2dec50d8c2b28d6cc7e4f041fbdfa4998aa1b5663b89', 'type':'l2v', 'chain':'violas'},
            ],
        'module':[
            {'address':'cd0476e85ecc5fa71b61d84b9cf2f7fd524689a4f870c46d6a5d901b5ac1fdb2', 'type':'v2b', 'chain':'violas'},
            {'address':'cd0476e85ecc5fa71b61d84b9cf2f7fd524689a4f870c46d6a5d901b5ac1fdb2', 'type':'b2v', 'chain':'violas'},
            {'address':'210a283f13e42a37b7fb2dec50d8c2b28d6cc7e4f041fbdfa4998aa1b5663b89', 'type':'v2l', 'chain':'violas'},
            {'address':'cd0476e85ecc5fa71b61d84b9cf2f7fd524689a4f870c46d6a5d901b5ac1fdb2', 'type':'l2v', 'chain':'violas'},
            ],
        'combine':[
            {'address':'1b3920fb9703cace285ac9ef5b54886b8b7a85442a8b38e06237908c3dfc1e5c', 'type':'v2b', 'chain':'violas'},
            {'address':'1b3920fb9703cace285ac9ef5b54886b8b7a85442a8b38e06237908c3dfc1e5c', 'type':'v2l', 'chain':'violas'},
            {'address':'1b3920fb9703cace285ac9ef5b54886b8b7a85442a8b38e06237908c3dfc1e5c', 'type':'l2v', 'chain':'libra'},
            {'address':'2N9gZbqRiLKAhYCBFu3PquZwmqCBEwu1ien', 'type':'b2v', 'chain':'btc'},
            ],
        }

looping_sleep={
        'v2b' : 1,          #violas token exchange btc thread loop time(s)
        'b2v' : 2,          #btc exchange violas token thread loop time(s)
        'v2l' : 3,
        'l2v' : 4,
        'vfilter' : 5,      #violas blockchain transactions filter
        'lfilter' : 6,
        'v2bproof' : 7,     #communication thread loop time
        'comm': 8,          #communication thread loop time
        }
