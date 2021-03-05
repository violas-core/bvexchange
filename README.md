# btc and vbtc exchange server 
btc violas token exchange

## depends
####use bitcoin >= 0.18 or violaslayer
##### btc opt
[bitcoin](https://github.com/bitcoin/bitcoin/tree/0.20)
violas nodes
[violaslayer](https://github.com/palliums-developers/violaslayer)

violaslayer:[https://github.com/palliums-developers/violaslayer]

##### violas or libra opt
violas-client: [https://github.com/palliums-developers/violas-client.git]
version:v0.30+

## To run (manual)
git clone https://github.com/palliums-developers/bvexchange
cd bvexchnge
git submodule init
git submodule update
./bvworkspace.sh
./bvmanage.py --conf ./bvexchange.toml --mod "all" ...

## Ubuntu
##Build requirements
sudo apt install python3.8 sqlite3 libsqlite3-dev redis
sudo python3 -m pip install bitcoinrpc sqlalchemy redis web3 sqlalchemy flask requests sqlite3 python3.8-dev gunicorn

## or 
cd violas-client/
pip3 install -r requirements.txt

git clone https://github.com/palliums-developers/bvexchange.git
cd bvexchange
sudo ./bvmanage.py --conf ./bvexchange.toml --mod "all"

# catalog
### bvmanage.py
    work run manage, main

### bvexchange.py
    work main file

### bvexchange.py
    work env change

### btc
    connect to bvlscore node and call rpc to work

### comm
    Definition of shared class

### db
    Database definition, operation

### exchange
    btc exchange vbtc, vbtc exchange btc operation

### log
    Log configuration and output classification

### libvioals/liblibra
    Dependent libraries(libra/violas)

### setting.py
    Main configuration file

### stmanage.py
    Manage configuration file

### test
    violas chain test 

### vlsopt
    violas related operations. violas client、server、wallet

### ethopt
    ethereum related operations. ethereum client、wallet

### vwallet
    violas wallet file

### analysis
    violas/libra transaction filter , state parse

### vrequest
    request transaction info from db

### tools
    violas chain init   

### webserver
    transaction record and address info webserver(flask)
    
####frame: nginx + gunicorn + flask
##### install
    install gunicorn: apt install gunicorn
    install flask: apt install flask==1.1.1
    install nginx: apt install nginx

##### config
###### nginx: 
    cp  violas_tranrecord  /etc/nginx/sites-available
    cd  /etc/nginx/sites-enabled
    ln -s /etc/nginx/sites-available/violas_tranrecord violas_tranrecord
##### start
###### gunicorn
    cd webserver
    ./start_gunicorn.sh

##### nginx
    sudo systemctl start nginx

