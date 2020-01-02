import logging.config

config = {
   'version': 1,
   'formatters': {
       'simple': {
           #'format': '%(asctime)s : %(name)s : %(levelname)s : %(message)s',
           'format':'%(asctime)s:%(levelname)s:%(threadName)s:%(thread)d:%(name)s:%(filename)s:%(lineno)d--: ''%(message)s' 
           },
       },
   'handlers': {
       'console': {
           'class': 'logging.StreamHandler',
           'level': 'DEBUG',
           'formatter': 'simple'
           },
       'file': {
           'class': 'logging.handlers.RotatingFileHandler',
           'filename': 'bvexchange.log',
           'level': 'DEBUG',
           'formatter': 'simple',
           'backupCount' : 3,
           'maxBytes' : 1000000 #1M
           },
       },
   'loggers':{
       
       'bvelog': {
           'handlers': ['console', 'file'],
           'level': 'DEBUG',
           },
       'exgb2v': {
           'handlers': ['console', 'file'],
           'level': 'DEBUG',
           },
       'exgv2b': {
           'handlers': ['console', 'file'],
           'level': 'DEBUG',
           },
       'dbv2b': {
           'handlers': ['console', 'file'],
           'level': 'DEBUG',
           },
       'dbb2v': {
           'handlers': ['console', 'file'],
           'level': 'DEBUG',
           },
       'dbvfilter': {
           'handlers': ['console', 'file'],
           'level': 'DEBUG',
           },
       'dbvproof': {
           'handlers': ['console', 'file'],
           'level': 'DEBUG',
           },
       'vclient': {
           'handlers': ['console', 'file'],
           'level': 'DEBUG',
           },
       'bclient': {
           'handlers': ['console', 'file'],
           'level': 'DEBUG',
           },
       'vproof': {
           'handlers': ['console', 'file'],
           'level': 'DEBUG',
           },
       'vfilter': {
           'handlers': ['console', 'file'],
           'level': 'DEBUG',
           },
       }
}

