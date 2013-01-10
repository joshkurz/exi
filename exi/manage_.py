#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import subprocess
from flask.ext.script import Shell, Manager
from helpers import CreateApp
from ext import db
import commands

manager = Manager(CreateApp())

@manager.command
def clean_pyc():
    """Removes all *.pyc files from the project folder"""
    clean_command = "find . -name *.pyc -delete".split()
    subprocess.call(clean_command)

manager.add_command('shell', Shell(make_context=lambda:{'app': app, 'db': db}))

prjRootPath = os.path.join(os.path.dirname(app.root_path))

@manager.command
def run():
    app.run()

@manager.command
def initdb():
    """Init/reset database."""

    db.drop_all()
    db.create_all()
    # Init/reset data.

    demo = Usr(
            name=u'demo', 
            email=u'demo@example.com', 
            password=u'123456', 
            role_id=USER,
            status_id=ACTIVE,
            user_detail=UserDetail(
                age=10,
                url=u'http://demo.example.com', 
                deposit=100.00,
                location=u'Hangzhou', 
                bio=u'Demo Guy is ... hmm ... just a demo guy.'),
            )
    admin = Usr(
            name=u'admin', 
            email=u'admin@example.com', 
            password=u'123456', 
            role_id=ADMIN,
            status_id=ACTIVE,
            user_detail=UserDetail(
                age=10,
                url=u'http://admin.example.com', 
                deposit=100.00,
                location=u'Hangzhou', 
                bio=u'admin Guy is ... hmm ... just a admin guy.'),
            )
    db.session.add(demo)
    db.session.add(admin)
    db.session.commit()

manager.add_option('-c', '--config',
                   dest="config",
                   required=False,
                   help="config file")

if __name__ == "__main__":
    manager.run()
