# -*- coding: utf-8 -*-
import os
from flask import Flask
#from flask.ext.pymongo import PyMongo
#from exi.db import db
from exi.settings import BaseConfig


class NoContextProcessorException(Exception):
    pass

class NoBlueprintException(Exception):
    pass

class NoExtensionException(Exception):
    pass

class CreateApp(object):

    def __init__(self, cfg=BaseConfig, envvar='PROJECT_SETTINGS', bind_db=True):
        self.app_config = cfg
        self.app_envvar = envvar
        self.bind_db = bind_db

    def get_app(self, app_module_name, **kwargs):
        self.app = Flask(app_module_name, **kwargs)
        self.app.config.from_object(self.app_config)
        self.app.config.from_envvar(self.app_envvar, silent=True)
        self.app.config.from_pyfile('local_settings.py', silent=True)

        self._bind_extensions()
        self._register_blueprints()
        self._register_context_processors()
        
        #self.app.db = db
        #connection = get_connection()
        #self.app.db = connection[self.app.config['MONGO_DBNAME']]
        
        return self.app

    def _get_imported_stuff_by_path(self, path):
        mo_pa = path.split('.')
        module_name = '.'.join(mo_pa[:-1])
        objNam = mo_pa[-1]
        module = __import__(module_name, fromlist=[objNam])

        return module, objNam

    def _bind_extensions(self):
        for ext_path in self.app.config.get('EXTENSIONS', []):
            module, e_name = self._get_imported_stuff_by_path(ext_path)
            if not hasattr(module, e_name):
                raise NoExtensionException('No {e_name} extension found'.format(e_name=e_name))
            ext = getattr(module, e_name)
            if getattr(ext, 'init_app', False):
                ext.init_app(self.app)
            else:
                ext(self.app)

    def _register_context_processors(self):
        for processor_path in self.app.config.get('CONTEXT_PROCESSORS', []):
            module, p_name = self._get_imported_stuff_by_path(processor_path)
            if hasattr(module, p_name):
                self.app.context_processor(getattr(module, p_name))
            else:
                raise NoContextProcessorException('No {cp_name} context processor found'.format(cp_name=p_name))

    def _register_blueprints(self):
        for blueprint_path in self.app.config.get('BLUEPRINTS', []):
            module, b_name = self._get_imported_stuff_by_path(blueprint_path)
            if hasattr(module, b_name):
                self.app.register_blueprint(getattr(module, b_name))
            else:
                raise NoBlueprintException('No {bp_name} blueprint found'.format(bp_name=b_name))


import datetime
import math
from flask import abort 


# Custom Template Filters
def datetimeformat(value):
    delta = datetime.datetime.now() - value
    if delta.days == 0:
        formatting = 'today'
    elif delta.days < 10:
        formatting = '{0} days ago'.format(delta.days)
    elif delta.days < 28:
        formatting = '{0} weeks ago'.format(int(math.ceil(delta.days/7.0)))
    elif value.year == datetime.datetime.now().year:
        formatting = 'on %d %b'
    else:
        formatting = 'on %d %b %Y'
    return value.strftime(formatting)

keyspace = "fw59eorpma2nvxb07liqt83_u6kgzs41-ycdjh"

def int_str(val):
    """ Turn a positive integer into a string. """
    assert val >= 0
    out = ""
    while val > 0:
        val, digit = divmod(val, len(keyspace))
        out += keyspace[digit]
    return out[::-1]

def str_int(val):
    """ Turn a string into a positive integer. """
    out = 0
    for c in val:
        out = out * len(keyspace) + keyspace.index(c)
    return out

def chaffify(val, chaff_val = 87953):
    """ Add chaff to the given positive integer. """
    return val * chaff_val

def dechaffify(chaffy_val, chaff_val = 87953):
    """ Dechaffs the given chaffed value. chaff_val must be the same as given to chaffify2(). If the value does not seem to be correctly chaffed, raises a ValueError. """
    val, chaff = divmod(chaffy_val, chaff_val)
    if chaff != 0:
        raise ValueError("Invalid chaff in value")
    return val

def get_or_abort(model, object_id, code=404):
        """
        get an object with his given id or an abort error (404 is the default)
        """
        result = model.query.get(object_id)
        return result or abort(code)

def encode_id(val):
    """
     Encodes ID into semi random set of strings
    """
    return int_str(chaffify(val))

def decode_id(val):
    return dechaffify(str_int(val))


