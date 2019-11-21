'''

bvexchange config
'''



#btc exchange violas token thread loop time(s)
b2v_sleep = 8

#violas token exchange btc thread loop time(s)
v2b_sleep = 6

#communication thread loop time
comm_sleep = 122

traceback_limit = 4

#db logging echo(False, True) default: False
db_echo=False

#btc connect 
btc_conn = {'rpcuser':'btc', 
        'rpcpassword':'btc', 
        'rpcip':'192.168.1.196', 
        'rpcport':9409}

#btc receiver address
receivers =['2NBtsptghCrd5b2RNbgDnkh6AFuQ46K5WUa', 
        '2MzG6Lxs3ATwiMuovVLPQsyejCDdgyYyF1F']
