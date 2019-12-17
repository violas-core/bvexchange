import logging.config

config = {
   'version': 1,
   'formatters': {
       'simple': {
           'format': '%(asctime)s : %(name)s : %(levelname)s : %(message)s',
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
       'b2vlog': {
           'handlers': ['console', 'file'],
           'level': 'DEBUG',
           },
       'v2blog': {
           'handlers': ['console', 'file'],
           'level': 'DEBUG',
           },
       'dbv2blog': {
           'handlers': ['console', 'file'],
           'level': 'DEBUG',
           },
       'dbb2vlog': {
           'handlers': ['console', 'file'],
           'level': 'DEBUG',
           },
       'blog': {
           'handlers': ['console', 'file'],
           'level': 'DEBUG',
           },
       'vlog': {
           'handlers': ['console', 'file'],
           'level': 'DEBUG',
           },
       }
}

