# -*- coding: utf-8 -*-

from flask import Flask, Blueprint, render_template, current_app, request, jsonify, redirect
from flask.ext.login import login_user, login_required, current_user, logout_user, confirm_login, login_fresh
from exi.helpers import CreateApp
from bson import ObjectId
from exi.db import db
from exi.models import User
from exi.ext import login_manager
from flask_pymongo_security.decorators import login_required, anonymous_user_required
from flask_pymongo_security.utils import url_for, login_user

users = Blueprint('users', __name__)

# @users.route('/users', methods=['GET', 'POST'])
# def index():
#     page = int(request.args.get('page', 1))
#     pagination = [] #User.query.paginate(page=page, per_page=10)
#     return render_template('users/index.html', pagination=pagination, current_user=current_user)

@users.route('/profile', methods=['GET', 'POST'])
def profile():
    return render_template('users/profile.html', current_user=current_user)

#@users.route('/register', methods=['GET', 'POST'])
#def register():
    #return render_template('security/register_user.html', current_user=current_user)


# def register(self, email, password='password'):
#     data = dict(email=email, password=password)
#     return self.client.post('/register', data=data, follow_redirects=True)
