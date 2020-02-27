#!/bin/bash 

export FLASK_APP=ws_request.py
export FLASK_ENV=development
flask run -h 0.0.0.0 -p 8088
