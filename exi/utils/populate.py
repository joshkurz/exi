# -*- coding: utf-8 -*-
from datetime import datetime
#from flask import current_app
from flask_pymongo_security.utils import encrypt_password
from werkzeug.local import LocalProxy
from exi.app import app

ds = LocalProxy(lambda: app.extensions['security'].datastore)

def create_roles(app):
    for role in ('admin', 'editor', 'author'):
        ds.create_role(name=role)
    ds.commit()

def create_users(app, count=None):
    users = [('matt@lp.com', 'password', ['admin'], True),
             ('joe@lp.com', 'password', ['editor'], True),
             ('dave@lp.com', 'password', ['admin', 'editor'], True),
             ('jill@lp.com', 'password', ['author'], True),
             ('tiya@lp.com', 'password', [], False)]
    count = count or len(users)

    for u in users[:count]:
        pw = encrypt_password(u[1])
        ds.create_user(email=u[0], password=pw,
                       roles=u[2], active=u[3], confirmed_at=datetime.utcnow())
    ds.commit()

def populate_data():
    create_roles(app)
    create_users(app)