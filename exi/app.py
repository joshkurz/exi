# -*- coding: utf-8 -*-
import sys, os

sys.path.pop(0)
# sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.abspath(__file__ + "/../../"))
# a hack until I make flask-pymongo-security and external package
sys.path.insert(0, os.path.join(os.path.abspath(__file__ + "/../../"), 'flask-pymongo-security'))

from flask.ext.assets import Bundle
from helpers import CreateApp
from settings import DevConfig
#from ext import assets
from flask.ext.mail import Mail
#from flask.ext.security import Security, UserMixin, RoleMixin
from flask_pymongo_security import Security, UserMixin, RoleMixin, PyMongoUserDatastore

app = CreateApp(DevConfig).get_app(__name__)
mail = Mail(app)

from exi.models import User, Role

# Setup Flask-Security
app.security = Security(app, PyMongoUserDatastore(User, Role))

def main():
    app.host = sys.argv['-h'] if '-h' in sys.argv else '127.0.0.1'
    if '-t' in sys.argv:
        app.config['TESTING'] = True
        print 'Running in test mode.'
    app.debug = '-d' in sys.argv
    app.use_reloader = '-r' in sys.argv
    app.run()
      
if __name__ == '__main__':
    main()
