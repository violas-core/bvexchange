#!/bin/bash

install_path=/usr/bin/bvexchange

mkdir $install_path

cp_mkdir() 
{
    mkdir -p $2
    cp -rf $1 $2
}
echo "copy db files"
cp_mkdir "db/*.py" "$install_path/db"

echo "copy btc files"
cp_mkdir "btc/*.py"  "$install_path/btc"

echo "copy violas files"
cp_mkdir "violas/*.py"  "$install_path/violas" 

echo "copy exchange files"
cp_mkdir "exchange/*.py"  "$install_path/exchange" 

echo "copy log files"
cp_mkdir "log/*.py"  "$install_path/log" 

echo "copy comm files"
cp_mkdir "comm/*.py"  "$install_path/comm" 

echo "copy test files"
cp_mkdir "test/*.py"  "$install_path/test" 

echo "copy packages files"
cp_mkdir "packages"  "$install_path" 

echo "copy root/*.py files"
cp_mkdir "*.py"  "$install_path" 
cp_mkdir "*.sh"  "$install_path" 

echo "copy bvexchange.service"
cp bvexchange.service /lib/systemd/system
