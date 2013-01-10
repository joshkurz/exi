# -*- coding: utf-8 -*-
from pymongo import Connection
from exi.settings import BaseConfig

try:
    from exi.local_settings import *
except:
    MONGO_HOST = BaseConfig.MONGO_HOST
    MONGO_DBNAME = BaseConfig.MONGO_DBNAME

db = Connection(MONGO_HOST)[MONGO_DBNAME]
