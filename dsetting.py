'''

bvexchange config
'''

traceback_limit = 4

#db logging echo(False, True) default: False
db_echo=False

#v2b max replay exchange count(state = faild)
v2b_maxtimes = 99

#btc connect 
btc_conn = {'user':'btc', 
        'password':'btc', 
        'host':'127.0.0.1', 
        'port':8066, 
        'domain':'violaslayer', 
        "server":"violaslayer"} #server(btc  violaslayer) default :btc 

#violas node list, to connect one
violas_nodes=[
        #{'name':'84', 'host':'52.27.228.84', "port":40001, 'faucet':'mint_test.key'},
        {'name':'84', 'host':'52.27.228.84', "port":40001},
        {'name':'242', 'host':'13.68.141.242', "port":40001},
        {'name':'50', 'host':'47.52.195.50', "port":40001}, 
        {'name':'235', 'host':'18.220.66.235', "port":40001},
        #{'host':'125.39.5.57', 'port':40001, 'faucet':'mint_tianjin.key', 'name':'tianjin'},
        #{'host':'192.168.31.18', 'port':8000, 'faucet':'mint_local.key', 'name':'local'},
        ]

#libra node list, to connect one
libra_nodes=[
         #{'host':'ac.testnet.libra.org', port: 8000, 'name':'libra'},
         {'host':'http://client.testnet.libra.org', 'name':'libra'},
        ]

#vioals server list. violas provides query of historical transactions. to connect one 
violas_servers=[
        {'host':'52.27.228.84', "port":4000, 'user':'violas', 'password':'violas'},
        ]

#db info type(vfilter vfilter lfilter v2b  l2b v2l)
db_list=[
        #remote
        #{'host':'18.136.139.151', 'port':6378, 'db':'lfilter', 'password':'af955c1d62a74a7543235dbb7fa46ed98948d2041dff67dfdb636a54e84f91fb', 'step':300},
        #{'host':'18.136.139.151', 'port':6378, 'db':'vfilter', 'password':'af955c1d62a74a7543235dbb7fa46ed98948d2041dff67dfdb636a54e84f91fb', 'step':300},
        #{'host':'18.136.139.151', 'port':6378, 'db':'bfilter', 'password':'af955c1d62a74a7543235dbb7fa46ed98948d2041dff67dfdb636a54e84f91fb', 'step':300},
        #{'host':'18.136.139.151', 'port':6378, 'db':'v2b', 'password':'af955c1d62a74a7543235dbb7fa46ed98948d2041dff67dfdb636a54e84f91fb', 'step':10},
        #{'host':'18.136.139.151', 'port':6378, 'db':'l2v', 'password':'af955c1d62a74a7543235dbb7fa46ed98948d2041dff67dfdb636a54e84f91fb', 'step':10},
        #{'host':'18.136.139.151', 'port':6378, 'db':'v2l', 'password':'af955c1d62a74a7543235dbb7fa46ed98948d2041dff67dfdb636a54e84f91fb', 'step':10},
        #{'host':'18.136.139.151', 'port':6378, 'db':'b2v', 'password':'af955c1d62a74a7543235dbb7fa46ed98948d2041dff67dfdb636a54e84f91fb', 'step':10},
        #{'host':'18.136.139.151', 'port':6378, 'db':'record', 'password':'af955c1d62a74a7543235dbb7fa46ed98948d2041dff67dfdb636a54e84f91fb', 'step':10},
        {'host':'127.0.0.1', 'port':6378, 'db':'lfilter', 'password':'violas', 'step':100},
        {'host':'127.0.0.1', 'port':6378, 'db':'vfilter', 'password':'violas', 'step':100},
        {'host':'127.0.0.1', 'port':6378, 'db':'bfilter', 'password':'violas', 'step':200},
        {'host':'127.0.0.1', 'port':6378, 'db':'v2b', 'password':'violas', 'step':10},
        {'host':'127.0.0.1', 'port':6378, 'db':'l2v', 'password':'violas', 'step':100},
        {'host':'127.0.0.1', 'port':6378, 'db':'v2l', 'password':'violas', 'step':100},
        {'host':'127.0.0.1', 'port':6378, 'db':'b2v', 'password':'violas', 'step':10},
        {'host':'127.0.0.1', 'port':6378, 'db':'record', 'password':'violas', 'step':100},
        ]

address_list = {
        #recever violas/libra coin
        'receiver':[
            ##vbtc -> btc
            {'address':'dcfa787ecb304c20ff24ed6b5519c2e5cae5f8464c564aabb684ecbcc19153e9', 'type':'v2b', 'chain':'violas'},
            ##vlibra -> libra
            {'address':'5f4d3d86949fafc804d6c457d9a92bf9ee1e24e8fc664894709c947b74823b2f', 'type':'v2l', 'chain':'violas'},
            ##libra -> vlibra
            {'address':'4a73cfd0365c641341a7a3bc376423480a82179351b8ecb6c5e68ab7b08622de', 'type':'l2v', 'chain':'libra'},
            ##btc -> vbtc
            {'address':'2MxBZG7295wfsXaUj69quf8vucFzwG35UWh', 'type':'b2v', 'chain':'btc'},
            {'address':'2N2YasTUdLbXsafHHmyoKUYcRRicRPgUyNB', 'type':'b2v', 'chain':'btc'},
            ],
        #send coin from this address
        'sender':[ 
            ##vbtc coin
            {'address':'270be97cae6bf9ecca084dfa6c7117badabe5de7fa81c906a5a23d5267138aa9', 'type':'b2v', 'chain':'violas'},
            ##btc coin
            {'address':'2N2YasTUdLbXsafHHmyoKUYcRRicRPgUyNB', 'type':'v2b', 'chain':'btc'},
            {'address':'2N9gZbqRiLKAhYCBFu3PquZwmqCBEwu1ien', 'type':'v2b', 'chain':'btc'},
            {'address':'2MxBZG7295wfsXaUj69quf8vucFzwG35UWh', 'type':'v2b', 'chain':'btc'},
            ##libra coin
            {'address':'c62da985e679fa642f51f84f694be65a8d3b6ca4b293491b63adf1dfc9754a33', 'type':'v2l', 'chain':'libra'},
            ##vlibra coin
            {'address':'7b102beb21460be85948a41bd2080265149bf4deff39f896c836a2760f6806b9', 'type':'l2v', 'chain':'violas'},
            ],
        #module address for type(violas nodes's vbtc or vlibra ...), type must be unique
        'module':[
            #vbtc module
            #{'address':'00000000000000000000000000000000e1be1ab8360a35a0259f1c93e3eac736', 'type':'v2b-old', 'chain':'violas'},
            {'address':'00000000000000000000000000000000e1be1ab8360a35a0259f1c93e3eac736', 'type':'v2b', 'chain':'violas'},
            {'address':'00000000000000000000000000000000e1be1ab8360a35a0259f1c93e3eac736', 'type':'b2v', 'chain':'btc'},
            #vbtc module
            {'address':'00000000000000000000000000000000e1be1ab8360a35a0259f1c93e3eac736', 'type':'b2v', 'chain':'violas'},
            #vlibra module
            {'address':'00000000000000000000000000000000e1be1ab8360a35a0259f1c93e3eac736', 'type':'v2l', 'chain':'violas'},
            {'address':'0000000000000000000000000000000000000000000000000000000000000000', 'type':'v2l', 'chain':'libra'},
            #vlibra module
            {'address':'0000000000000000000000000000000000000000000000000000000000000000', 'type':'l2v', 'chain':'libra'},
            {'address':'00000000000000000000000000000000e1be1ab8360a35a0259f1c93e3eac736', 'type':'l2v', 'chain':'violas'},
            ],
        #module address for type(violas nodes's vbtc or vlibra ...), type must be unique
        'token':[
            #vbtc owner
            {'address':'03d3bbb134e5d31b194d910e2d94e37ca0dd2abf254d09de85d49290250a8190', 'tokenid': 2, "tokenname":"vbtc",'type':'v2b', 'chain':'violas'},
            {'address':'03d3bbb134e5d31b194d910e2d94e37ca0dd2abf254d09de85d49290250a8190', 'tokenid': 2, "tokenname":"vbtc", 'type':'b2v', 'chain':'violas'},
            #vlibra owner
            {'address':'1eaa12e8c4f196c24ed88ac5f472f128c7ef87304c0b9e477f17dcfd69abd0bb', 'tokenid': 3, "tokenname":"vlibra", 'type':'v2l', 'chain':'violas'},
            {'address':'1eaa12e8c4f196c24ed88ac5f472f128c7ef87304c0b9e477f17dcfd69abd0bb', 'tokenid': 3, "tokenname":"vlibra", 'type':'l2v', 'chain':'violas'},
            ],
        #combine coins to 
        'combine':[
            #vbtc
            {'address':'b93bb580bfba22c6d06ba5baac329b0c23e5d616f55614100b83ddece7a4c005', 'type':'v2b', 'chain':'violas'},
            {'address':'4a5a4d3fa63633fbecfd50a17b4b5a38dfbac8a5a08be9e4b958b4aeb9e8f0ea', 'type':'v2l', 'chain':'violas'},
            #vlibra
            {'address':'47535b0273d05a3689680409b18c76db4a5d8ad92880cf11fcbed74310b67bfc', 'type':'l2v', 'chain':'libra'},
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
