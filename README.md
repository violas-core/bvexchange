# btc and vbtc exchange server 
btc violas token exchange

## depends
bvlscore: [https://github.com/palliums-developers/bvlscore.git]
violas nodes:[]
version:v0.5.0

violas-client: [https://github.com/palliums-developers/violas-client.git]
version:v4.0

## To run
git clone https://github.com/palliums-developers/bvexchange
cd bvexchnge
./redis_start.sh
./bvmanage.py --mod "all" :all  vfilter vproof v2b b2v ...

## Ubuntu
##Build requirements
sudo apt install python3.6 sqlite3 redis-server python3
python3 install python3.6-dev
pip3 install python-bitcoinrpc sqlalchemy redis5.0.7

cd violas-client/
pip3 install -r requirements.txt

git clone https://github.com/palliums-developers/bvexchange.git
cd bvexchange
./bvexchnge.py  or python3 bvexchange.py

# catalog
### bvmanage.py
    work run manage, main

### bvexchange.py
    work main file

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

### vwallet
    violas wallet file

### analysis
    violas/libra transaction filter , state parse

### vrequest
    request transaction info from db

### tools
    violas chain init   

### webserver
    transaction record webserver(flask)
    
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

