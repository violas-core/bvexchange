'''

bvexchange config
'''



#btc exchange violas token thread loop time(s)
b2v_sleep = 8

#violas token exchange btc thread loop time(s)
v2b_sleep = 6

#communication thread loop time
comm_sleep = 12

traceback_limit = 4

#db logging echo(False, True) default: False
db_echo=False

#btc connect 
btc_conn = {'rpcuser':'btc', 
        'rpcpassword':'btc', 
        'rpcip':'192.168.1.196', 
        'rpcport':9409}

#btc receiver address
receivers =['2NGQjMnVhwVVzw1Sq7vjAz9Rf7Z1Fv8LFsV']
# receiver address  state change to "end"
combineaddress='2N8qe3KogEF3DjWNsDGr2qLQGgQD3g9oTnc'

violas_nodes=[
        {'ip':'51.140.241.96', "port":40001, 'validator':'consensus_peers.config.toml', 'faucet':'temp_faucet_keys'},
        {'ip':'18.220.66.235', "port":40001, 'validator':'consensus_peers.config.toml', 'faucet':'temp_faucet_keys'},
        {'ip':'47.91.104.150', "port":40001, 'validator':'consensus_peers.config.toml', 'faucet':'temp_faucet_keys'},
        {'ip':'52.27.228.84', "port":40001, 'validator':'consensus_peers.config.toml', 'faucet':'temp_faucet_keys'},
        {'ip':'52.27.228.84', "port":40001, 'validator':'consensus_peers.config.toml', 'faucet':'temp_faucet_keys'}
        ]

#receiver address 
violas_recever="cd0476e85ecc5fa71b61d84b9cf2f7fd524689a4f870c46d6a5d901b5ac1fdb2"
#sendor address
violas_sender="210a283f13e42a37b7fb2dec50d8c2b28d6cc7e4f041fbdfa4998aa1b5663b89"
#btc module address
module_address="cd0476e85ecc5fa71b61d84b9cf2f7fd524689a4f870c46d6a5d901b5ac1fdb2"
