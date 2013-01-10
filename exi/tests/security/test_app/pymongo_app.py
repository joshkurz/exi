# -*- coding: utf-8 -*-

import sys
import os
from exi.db import db
from exi.models import User, Role

sys.path.pop(0)
sys.path.insert(0, os.getcwd())

from flask_pymongo_security import Security, UserMixin, RoleMixin, PyMongoUserDatastore

from exi.tests.security.test_app import create_app as create_base_app, populate_data, add_context_processors

def create_app(config, **kwargs):
    app = create_base_app(config)

    @app.before_first_request
    def before_first_request():
        names = [name for name in db.collection_names() \
            if 'system.' not in name]
        [db.drop_collection(name) for name in names]

        populate_data(app.config.get('USER_COUNT', None))

    app.security = Security(app, datastore=PyMongoUserDatastore(User, Role), **kwargs)

    add_context_processors(app.security)

    return app

if __name__ == '__main__':
    create_app({}).run()
