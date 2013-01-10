# -*- coding: utf-8 -*-
from flask import Blueprint


users = Blueprint('users', __name__,
                 template_folder='templates',
                 url_prefix='/users')

from forms import *
from views import *
