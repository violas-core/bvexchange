#!/bin/bash 

export FLASK_APP=ws_request.py
flask run -h 0.0.0.0 -p 5000
