##bvexchange config
#
#traceback_limit = 4
#
##db logging echo(False, True) default: False
#db_echo=False
#
##v2b max replay exchange count(state = faild)
#v2b_maxtimes = 99
#
##btc connect 
##btc_conn = {'rpcuser':'btc', 'rpcpassword':'btc', 'rpcip':'127.0.0.1', 'rpcport':18332}
#btc_conn = {'user':'btc', 
#        'password':'btc', 
#        'host':'127.0.0.1', 
#        'port':8066, 
#        'domain':'violaslayer', 
#        "server":"violaslayer"} #server(btc  violaslayer) default :btc 
#
##violas node list, to connect one
#violas_nodes=[
#        {'host':'52.151.2.66',     'port':40001, 'name':'violas 1'},
#        {'host':'52.151.9.191',    'port':40001, 'name':'violas 2'},
#        {'host':'52.229.12.97',    'port':40001, 'name':'violas 3'}, 
#        {'host':'52.183.33.162',   'port':40001, 'name':'violas 4'},
#        {'host':'13.77.137.84',    'port':40001, 'name':'violas 5'},
#        {'host':'http://ac.testnet.violas.io',   'port':40001, 'name':'violas 0'},
#        ]
#
##libra node list, to connect one
#libra_nodes=[
#         {'host':'http://client.testnet.libra.org', 'name':'libra'},
#        ]
#
##vioals server list. violas provides query of historical transactions. to connect one 
#violas_servers=[
#        {'host':'52.27.228.84', "port":4000, 'user':'violas', 'password':'violas'},
#        ]
#
##db info type(vfilter vfilter lfilter v2b  l2b v2l)
#db_list=[
#        #remote
#        {'host':'127.0.0.1', 'port':6378, 'db':'lfilter', 'password':'af955c1d62a74a7543235dbb7fa46ed98948d2041dff67dfdb636a54e84f91fb', 'step':500},
#        {'host':'127.0.0.1', 'port':6378, 'db':'vfilter', 'password':'af955c1d62a74a7543235dbb7fa46ed98948d2041dff67dfdb636a54e84f91fb', 'step':300},
#        {'host':'127.0.0.1', 'port':6378, 'db':'bfilter', 'password':'af955c1d62a74a7543235dbb7fa46ed98948d2041dff67dfdb636a54e84f91fb', 'step':300},
#        {'host':'127.0.0.1', 'port':6378, 'db':'v2b', 'password':'af955c1d62a74a7543235dbb7fa46ed98948d2041dff67dfdb636a54e84f91fb', 'step':10},
#        {'host':'127.0.0.1', 'port':6378, 'db':'l2v', 'password':'af955c1d62a74a7543235dbb7fa46ed98948d2041dff67dfdb636a54e84f91fb', 'step':10},
#        {'host':'127.0.0.1', 'port':6378, 'db':'v2l', 'password':'af955c1d62a74a7543235dbb7fa46ed98948d2041dff67dfdb636a54e84f91fb', 'step':10},
#        {'host':'127.0.0.1', 'port':6378, 'db':'b2v', 'password':'af955c1d62a74a7543235dbb7fa46ed98948d2041dff67dfdb636a54e84f91fb', 'step':10},
#        {'host':'127.0.0.1', 'port':6378, 'db':'record', 'password':'af955c1d62a74a7543235dbb7fa46ed98948d2041dff67dfdb636a54e84f91fb', 'step':10},
#        ]
#
#address_list = {
#        #recever violas/libra coin
#        'receiver':[
#            ##vbtc -> btc
#            {'address':'dcfa787ecb304c20ff24ed6b5519c2e5cae5f8464c564aabb684ecbcc19153e9', 'type':'v2b', 'chain':'violas'},
#            ##vlibra -> libra
#            {'address':'5f4d3d86949fafc804d6c457d9a92bf9ee1e24e8fc664894709c947b74823b2f', 'type':'v2l', 'chain':'violas'},
#            ##libra -> vlibra
#            #{'address':'4a73cfd0365c641341a7a3bc376423480a82179351b8ecb6c5e68ab7b08622de', 'type':'l2v', 'chain':'libra'},
#            {'address':'c16af35c8082f78399bedabfd1ec8c409334bb5e39e5919e081b6db72482e139', 'type':'l2v', 'chain':'libra', 'network':"ex"},
#            ##btc -> vbtc
#            {'address':'2MyMHV6e4wA2ucV8fFKzXSEFCwrUGr2HEmY', 'type':'b2v', 'chain':'btc'},
#            ],
#        #send coin from this address
#        'sender':[ 
#            ##vbtc coin
#            {'address':'270be97cae6bf9ecca084dfa6c7117badabe5de7fa81c906a5a23d5267138aa9', 'type':'b2v', 'chain':'violas'},
#            ##btc coin
#            {'address':'2MwBFJJn1f5Sg242D3wNUinKUCKS3GzCn7j', 'type':'v2b', 'chain':'btc'},
#            {'address':'2MyMHV6e4wA2ucV8fFKzXSEFCwrUGr2HEmY', 'type':'v2b', 'chain':'btc'},
#            {'address':'2N9fQcit5KB8vJHmBF5Z4DkUUTCgJA8GKb3', 'type':'v2b', 'chain':'btc'},
#            ##libra coin
#            #{'address':'c62da985e679fa642f51f84f694be65a8d3b6ca4b293491b63adf1dfc9754a33', 'type':'v2l', 'chain':'libra'},
#            {'address':'7d572ec38dd124ad4faec3fc077217efab88cc9dd86f72d8816b3cabf155eb86', 'type':'v2l', 'chain':'libra'},
#            ##vlibra coin
#            {'address':'7b102beb21460be85948a41bd2080265149bf4deff39f896c836a2760f6806b9', 'type':'l2v', 'chain':'violas'},
#            ],
#        #module address for type(violas nodes's vbtc or vlibra ...), type must be unique
#        'module':[
#            #vbtc module
#            {'address':'00000000000000000000000000000000e1be1ab8360a35a0259f1c93e3eac736', 'type':'v2b', 'chain':'violas'},
#            {'address':'00000000000000000000000000000000e1be1ab8360a35a0259f1c93e3eac736', 'type':'b2v', 'chain':'btc'},
#            #vbtc module
#            {'address':'00000000000000000000000000000000e1be1ab8360a35a0259f1c93e3eac736', 'type':'b2v', 'chain':'violas'},
#            #vlibra module
#            {'address':'00000000000000000000000000000000e1be1ab8360a35a0259f1c93e3eac736', 'type':'v2l', 'chain':'violas'},
#            {'address':'0000000000000000000000000000000000000000000000000000000000000000', 'type':'v2l', 'chain':'libra'},
#            #vlibra module
#            {'address':'0000000000000000000000000000000000000000000000000000000000000000', 'type':'l2v', 'chain':'libra'},
#            {'address':'00000000000000000000000000000000e1be1ab8360a35a0259f1c93e3eac736', 'type':'l2v', 'chain':'violas'},
#            ],
#        #module address for type(violas nodes's vbtc or vlibra ...), type must be unique
#        'token':[
#            #vbtc owner
#            {'address':'03d3bbb134e5d31b194d910e2d94e37ca0dd2abf254d09de85d49290250a8190', 'tokenid': 5, "tokenname":"vbtc",'type':'v2b', 'chain':'violas'},
#            {'address':'03d3bbb134e5d31b194d910e2d94e37ca0dd2abf254d09de85d49290250a8190', 'tokenid': 5, "tokenname":"vbtc", 'type':'b2v', 'chain':'violas'},
#            #vlibra owner
#            {'address':'1eaa12e8c4f196c24ed88ac5f472f128c7ef87304c0b9e477f17dcfd69abd0bb', 'tokenid': 6, "tokenname":"vlibra", 'type':'v2l', 'chain':'violas'},
#            {'address':'1eaa12e8c4f196c24ed88ac5f472f128c7ef87304c0b9e477f17dcfd69abd0bb', 'tokenid': 6, "tokenname":"vlibra", 'type':'l2v', 'chain':'violas'},
#            ],
#        #combine coins to 
#        'combine':[
#            #vbtc
#            {'address':'b93bb580bfba22c6d06ba5baac329b0c23e5d616f55614100b83ddece7a4c005', 'type':'v2b', 'chain':'violas'},
#            {'address':'4a5a4d3fa63633fbecfd50a17b4b5a38dfbac8a5a08be9e4b958b4aeb9e8f0ea', 'type':'v2l', 'chain':'violas'},
#            #vlibra
#            #{'address':'47535b0273d05a3689680409b18c76db4a5d8ad92880cf11fcbed74310b67bfc', 'type':'l2v', 'chain':'libra'},
#            {'address':'ed997d48192d313deda1d0335722a9bf231bded0afc5ff71c3882b4865cc2f0b', 'type':'l2v', 'chain':'libra'},
#            {'address':'2N9fQcit5KB8vJHmBF5Z4DkUUTCgJA8GKb3', 'type':'b2v', 'chain':'btc'},
#            ],
#        }
#
#looping_sleep={
#        'v2b' : 1,          #violas token exchange btc thread loop time(s)
#        'b2v' : 1,          #btc exchange violas token thread loop time(s)
#        'v2l' : 1,
#        'l2v' : 1,
#        'vfilter' : 0,      #violas blockchain transactions filter
#        'lfilter' : 0,
#        'v2bproof' : 1,     #communication thread loop time
#        'v2lproof' : 1,     #communication thread loop time
#        'comm': 8,          #communication thread loop time
#        }
#
from tomlbase import tomlbase

class tomlopt(tomlbase):
    def __init__(self, tomlfile):
        super().__init__(tomlfile)

    @property
    def looping_sleep(self):
        return self.get("looping_sleep")

    @property
    def db_list(self):
        return self.get("db_list")

    @property
    def btc_conn(self):
        return self.get("btc_conn")

    @property
    def traceback_limit(self):
        return self.get("traceback_limit")

    @property
    def db_echo(self):
        return self.get("db_echo")

    @property
    def v2b_maxtimes(self):
        return self.get("v2b_maxtimes")

    @property
    def violas_nodes(self):
        return self.get("violas_nodes")

    @property
    def libra_nodes(self):
        return self.get("libra_nodes")

    @property
    def violas_servers(self):
        return self.get("violas_servers")

    @property
    def address_list(self):
        return self.get("address_list")

    @property
    def token_map(self):
        return self.get("token_map")

    @property
    def type_stable_token(self):
        return self.get("type_stable_token")

    @property
    def type_lbr_token(self):
        return self.get("type_lbr_token")

    @property
    def support_token_id(self):
        return self.get("support_token_id")

    @property
    def type_token(self):
        return self.get("type_token")

    @property
    def swap_module(self):
        return self.get("type_token")
setting = tomlopt("bvexchange.toml")

