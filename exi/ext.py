# -*- coding: utf-8 -*-
from flask.ext.debugtoolbar import DebugToolbarExtension
from flask.ext.login import LoginManager
# from flask.ext.assets import Environment

# assets = Environment()
login_manager = LoginManager()

toolbar = lambda app: DebugToolbarExtension(app)
