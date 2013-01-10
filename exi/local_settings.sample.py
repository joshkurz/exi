# -*- coding: utf-8 -*-

TESTING = False
DEBUG = False
CSRF_ENABLED = True
    
MONGO_HOST              = 'localhost'
MONGO_PORT              = 27017
MONGO_DBNAME            = 'exi-test'
MONGO_USERNAME          = None
MONGO_PASSWORD          = None    


SECRET_KEY              = 'super-secret'
DEFAULT_MAIL_SENDER     = 'name@domain.com'


MAIL_SERVER             = 'smtp.gmail.com'
MAIL_PORT               = 465
MAIL_USE_TLS            = False
MAIL_USE_SSL            = True
MAIL_USERNAME           = 'name@domain.com'
MAIL_PASSWORD           = 'xxxxxxxx'

SECURITY_REGISTERABLE   = True
SECURITY_CONFIRMABLE    = True
SECURITY_RECOVERABLE    = True