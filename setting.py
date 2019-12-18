'''

bvexchange config
'''



#btc exchange violas token thread loop time(s)
b2v_sleep = 8

#violas token exchange btc thread loop time(s)
v2b_sleep = 6

#communication thread loop time
comm_sleep = 1

traceback_limit = 4

#db logging echo(False, True) default: False
db_echo=False

#btc connect 
btc_conn = {'rpcuser':'btc', 
        'rpcpassword':'btc', 
        'rpcip':'192.168.1.196', 
        'rpcport':18332}

#btc receiver address, btc exchange vbtc's valid receiving address, filter btc proofs
btc_receivers =['2MxBZG7295wfsXaUj69quf8vucFzwG35UWh', '2N2YasTUdLbXsafHHmyoKUYcRRicRPgUyNB']
# receiver address  state change to "end", combineaddress not in receivers 
btc_combineaddress='2N9gZbqRiLKAhYCBFu3PquZwmqCBEwu1ien'
#btc send address. vbtc exchange btc use. from sender send btc to target address. (must has privkey)
btc_senders=['2N2YasTUdLbXsafHHmyoKUYcRRicRPgUyNB','2N9gZbqRiLKAhYCBFu3PquZwmqCBEwu1ien', '2MxBZG7295wfsXaUj69quf8vucFzwG35UWh']

#violas node list, to connect one
violas_nodes=[
        {'ip':'51.140.241.96', "port":40001, 'validator':'consensus_peers.config.toml', 'faucet':'faucet_keys'},
        {'ip':'13.68.141.242', "port":40001, 'validator':'consensus_peers.config.toml', 'faucet':'faucet_keys'},
        {'ip':'47.52.195.50', "port":40001, 'validator':'consensus_peers.config.toml', 'faucet':'faucet_keys'},
        {'ip':'18.220.66.235', "port":40001, 'validator':'consensus_peers.config.toml', 'faucet':'faucet_keys'},
        {'ip':'52.27.228.84', "port":40001, 'validator':'consensus_peers.config.toml', 'faucet':'faucet_keys'},
        ]

#vioals server list. violas provides query of historical transactions. to connect one 
violas_servers=[
        {'ip':'52.27.228.84', "port":4000, 'user':'violas', 'password':'violas'},
        ]

#violas receiver address, vbtc exchange btc's valid receiving address, filter transaction 
violas_receivers=['1b3920fb9703cace285ac9ef5b54886b8b7a85442a8b38e06237908c3dfc1e5c']
#violas sendor address, btc exchange vbtc use. from violas_sender send vbtc to target address. (must has privkey)
violas_sender='210a283f13e42a37b7fb2dec50d8c2b28d6cc7e4f041fbdfa4998aa1b5663b89'
#btc module address(vbtc module address)
module_address='cd0476e85ecc5fa71b61d84b9cf2f7fd524689a4f870c46d6a5d901b5ac1fdb2'
#v2b max replay exchange count(state = faild)
v2b_maxtimes = 99999
