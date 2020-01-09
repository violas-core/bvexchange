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
       }
}

