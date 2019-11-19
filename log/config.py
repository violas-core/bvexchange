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
           'level': 'ERROR',
           'formatter': 'simple',
           'backupCount' : 3,
           'maxBytes' : 1000000 #1M
           },
       # 其他的 handler
       },
   'loggers':{
       #'StreamLogger': {
       #    'handlers': ['console'],
       #    'level': 'DEBUG',
       #    },
       'bvelog': {
           # 既有 console Handler，还有 file Handler
           'handlers': ['console', 'file'],
           'level': 'DEBUG',
           },
       # 其他的 Logger
       }
}

