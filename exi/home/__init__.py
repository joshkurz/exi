# -*- coding: utf-8 -*-
from flask import Blueprint


home = Blueprint('home', __name__,
                 template_folder='templates',
                 url_prefix='/')

from forms import *
from views import *
