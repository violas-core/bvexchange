#!/bin/bash

#redis-server ./violas_filter.conf
redis-server --port 6378 --dbfilename redis_violas.rdb --requirepass violas
