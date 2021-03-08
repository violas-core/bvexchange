#!/bin/bash
gunicorn -c gunicorn.conf.py fs_request:app
