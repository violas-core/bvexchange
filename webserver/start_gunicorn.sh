#!/bin/bash
gunicorn -w 4 -b 0.0.0.0:8088 ws_request:app
