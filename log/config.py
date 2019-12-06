import logging.config

config = {
   'version': 1,
   'formatters': {
       'simple': {
           'format': '%(asctime)s : %(name)s : %(levelname)s : %(message)s',
           },
       # 其他的 formatter
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
       # 其他的 handler
       },
   'loggers':{
       
       'bvelog': {
           # 既有 console Handler，还有 file Handler
           'handlers': ['console', 'file'],
           'level': 'DEBUG',
           },
       'b2vlog': {
           # 既有 console Handler，还有 file Handler
           'handlers': ['console', 'file'],
           'level': 'DEBUG',
           },
       'v2blog': {
           # 既有 console Handler，还有 file Handler
           'handlers': ['console', 'file'],
           'level': 'DEBUG',
           },
       'dbv2blog': {
           # 既有 console Handler，还有 file Handler
           'handlers': ['console', 'file'],
           'level': 'DEBUG',
           },
       'dbb2vlog': {
           # 既有 console Handler，还有 file Handler
           'handlers': ['console', 'file'],
           'level': 'DEBUG',
           },
       'blog': {
           # 既有 console Handler，还有 file Handler
           'handlers': ['console', 'file'],
           'level': 'DEBUG',
           },
       'vlog': {
           # 既有 console Handler，还有 file Handler
           'handlers': ['console', 'file'],
           'level': 'DEBUG',
           },
        
       # 其他的 Logger
       }
}

