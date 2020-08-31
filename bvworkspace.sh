#!/bin/bash


rm_file(){
    if [ -f "$1" ]
    then
        rm $1
    fi
}

lns_file(){
    if [ -f "$1" ]
    then
        ln -s "$1" "$2"
    else
        echo "not found $2"
    fi
}

update_ln_fils(){
    rm_file $2
    lns_file $@
}
use_internal(){
    echo "call use_internal"
    update_ln_fils "datas/config/bvexchange_internal.toml" "bvexchange.toml"
    update_ln_fils "datas/wallet/bwallet" "bwallet"
    update_ln_fils "datas/wallet/vwallet_internal" "vwallet"
    update_ln_fils "datas/keys/mint_internal.key" "mint_test.key"
    update_ln_fils "datas/redis/redis_internal.conf" "redis.conf"
    update_ln_fils "datas/redis/redis_internal_start.sh" "redis_start"
}

use_external(){
    echo "call use_external"
    update_ln_fils "datas/config/bvexchange_external.toml" "bvexchange.toml"
    update_ln_fils "datas/wallet/bwallet" "bwallet"
    update_ln_fils "datas/wallet/vwallet_external" "vwallet"
    update_ln_fils "datas/keys/mint_external.key" "mint_test.key"
    update_ln_fils "datas/redis/redis_external.conf" "redis.conf"
    update_ln_fils "datas/redis/redis_external_start.sh" "redis_start"
}

change_workspace(){
    if [ $1 == 1 ]
    then
        use_internal
    elif [ $1 == 2 ]
    then
        use_external
    else
        echo "select index:"
        echo "  internal: 1"
        echo "  external: 2"
        return -1
    fi
    return 0
}

reselect(){
    count=0
    max_count=3
    while (( $count < $max_count ))
    do
        echo "select index:"
        echo "  internal: 1"
        echo "  external: 2"
        read -p "input 1 or 2: " sel_val
        echo $sel_val
        change_workspace $sel_val
        if [ $? == 0 ] ; then break; fi
        let count++
    done
}

echo $#
if [ $# == 0 ]
then
    reselect
elif [ $# == 1 ]
then
    if [ $1 == "internal" ]
    then
        use_internal
    elif [$1 == "external" ]
    then
        use_external
    else
        echo "args is invalid. can use args: internal external"
        return
    fi
else
    echo "args is invalid. can use args: internal external"
fi

