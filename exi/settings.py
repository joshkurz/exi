# -*- coding: utf-8 -*-
import os

class BaseConfig(object):

    # Get app root path
    # ../../configs/config.py

    _basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    PROJECT = "exi"
    DEBUG = False
    TESTING = False

    HOME_PATH           = 'C:/Users/Larry/__prjs/_fx/exi/exi/'

    LOG_FILE            = 'C:/Users/Larry/__prjs/_fx/exi/exi/logs/exi.log'
    LOG_LEVEL           = 'debug'

    DEFAULT_MAIL_SENDER = ("mail manager", "mail@manager.com")
    SECRET_KEY          = '5WOGba[U\\^yGXA6"^^a+9|Nx|xfF\:U;N_[U\\'

    CSRF_ENABLED = True
    DEBUG_TB_PROFILER_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False
        
    # ===========================================
    # Flask-babel
    #
    ACCEPT_LANGUAGES = ['es']
    BABEL_DEFAULT_LOCALE = 'en'

    # ===========================================
    # Flask-cache
    #
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 60


    MONGO_HOST          = 'localhost'
    MONGO_PORT          = 27017
    MONGO_DBNAME        = PROJECT
    MONGO_USERNAME      = None
    MONGO_PASSWORD      = None    

    DEFAULT_MAIL_SENDER     = 'info@yoursite.com'

    MAIL_SERVER             = 'smtp.gmail.com'
    MAIL_PORT               = 465
    MAIL_USE_TLS            = False
    MAIL_USE_SSL            = True
    MAIL_USERNAME           = 'info@yoursite.com'
    MAIL_PASSWORD           = 'password'

    # os.urandom(24)
    SECRET_KEY = 'secret key'

    BLUEPRINTS = [  #'api.api',
                    'exi.home.home',
                    'exi.users.users',
                    ]

    EXTENSIONS = [
                  #'exi.ext.assets',
                  'exi.ext.login_manager',
                  'exi.ext.toolbar',
                  ]

    CONTEXT_PROCESSORS = [
        'exi.home.context_processors.common_context',
        'exi.home.context_processors.navigation',
        'exi.home.context_processors.common_forms',
                          ]


class DevConfig(BaseConfig):

    DEBUG = True

    DEBUG_TB_PROFILER_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
        
    MONGO_HOST          = 'localhost'
    MONGO_PORT          = 27017
    MONGO_DBNAME        = BaseConfig.PROJECT + '-test'
    MONGO_USERNAME      = None
    MONGO_PASSWORD      = None    


    # ===========================================
    # Flask-mail
    #
    # Should be imported from env var.
    # https://bitbucket.org/danjac/flask-mail/issue/3/problem-with-gmails-smtp-server
    MAIL_DEBUG = DEBUG
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'gmail_username'
    MAIL_PASSWORD = 'gmail_password'
    DEFAULT_MAIL_SENDER = '%s@gmail.com' % MAIL_USERNAME

    # You should overwrite in production.py
    # Limited the maximum allowed payload to 16 megabytes.
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    USER_AVATAR_UPLOAD_FOLDER = "/tmp/uploads"
    #USER_AVATAR_UPLOAD_FOLDER = os.path.join(BaseConfig._basedir, 'uploads')


class TestConfig(BaseConfig):
    TESTING = True
    DEBUG = False
    CSRF_ENABLED = False
        
    MONGO_HOST          = 'localhost'
    MONGO_PORT          = 27017
    MONGO_DBNAME        = BaseConfig.PROJECT + '-test'
    MONGO_USERNAME      = None
    MONGO_PASSWORD      = None    


    MAIL_SERVER             = None
    MAIL_PORT               = None
    MAIL_USE_TLS            = None
    MAIL_USE_SSL            = None
    MAIL_USERNAME           = None
    MAIL_PASSWORD           = None

