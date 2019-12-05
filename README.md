# exchangebv
btc violas token exchange

#depends
bvlscore: [https://github.com/palliums-developers/bvlscore.git]
violas nodes
violas server: [https://github.com/palliums-developers/violas-webservice.git]

# install
apt install python3.6 sqlite3
python3.6 -m pip install --upgrade pip
pip3 install python-bitcoinrpc sqlalchemy
python3 install python3.6-dev

git clone https://github.com/palliums-developers/bvexchange.git
cd bvexchange
./bvexchnge.py  or python3 bvexchange.py


#catalog
##bvexchange.py
    work main file

##btc
    connect to bvlscore node and call rpc to work

##comm
    Definition of shared class

##db
    Database definition, operation

##exchange
    btc exchange vbtc, vbtc exchange btc operation

##log
    Log configuration and output classification

##packages
    Dependent libraries(libra)

##setting.py
    Main configuration file

##test
    test 

##violas
    violas related operations. violas client、server、wallet

#vwallet
    violas wallet file
