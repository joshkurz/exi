# -*- coding: utf-8 -*-

from flask import Flask, Blueprint, render_template, current_app, request, jsonify, redirect
from flask.ext.login import login_user, login_required, current_user, logout_user, confirm_login, login_fresh
#from flaskext.babel import gettext as _

#from forms import SignupForm, LoginForm, RecoverPasswordForm, ReauthForm, ChangePasswordForm

from exi.helpers import CreateApp
from bson import ObjectId
from exi.db import db
from exi.models import User
from exi.ext import login_manager
from flask_pymongo_security.decorators import login_required, anonymous_user_required, roles_required, roles_accepted
from flask_pymongo_security.utils import url_for, login_user

home = Blueprint('home', __name__)


@login_manager.user_loader
def load_user(id):
    return User().find_one(dict(_id=ObjectId(id)))

    
@home.route('/', methods=['GET', 'POST'])
def index():
    page = int(request.args.get('page', 1))
    pagination = [] #User.query.paginate(page=page, per_page=10)
    return render_template('home/index.html', current_user=current_user, content='Home Page')


#@home.route('/search')
#def search():
    #keywords = request.args.get('keywords', '').strip()
    #pagination = None
    #if keywords:
        #page = int(request.args.get('page', 1))
        #pagination = User.search(keywords).paginate(page, 1)
    #else:
        #flash(_('Please input keyword(s)'), 'error')
    #return render_template('home/search.html', pagination=pagination, keywords=keywords)

    
#@anonymous_user_required
#def login():
    #if current_user.is_authenticated():
        #return redirect(url_for('user.index'))

    #form = LoginForm(login=request.args.get('login', None),
                     #next=request.args.get('next', None))

    #if form.validate_on_submit():
        #user, authenticated = User.authenticate(form.login.data,
                                    #form.password.data)

        #if user and authenticated:
            #remember = request.form.get('remember') == 'y'
            #if login_user(user, remember=remember):
                #flash(_("Logged in"), 'success')
            #return redirect(form.next.data or url_for('user.index'))
        #else:
            #flash(_('Sorry, invalid login'), 'error')

    #return render_template('home/login.html', form=form)


#@home.route('/reauth', methods=['GET', 'POST'])
#@login_required
#def reauth():
    #form = ReauthForm(next=request.args.get('next'))

    #if request.method == 'POST':
        #user, authenticated = User.authenticate(current_user.name,
                                    #form.password.data)
        #if user and authenticated:
            #confirm_login()
            #current_app.logger.debug('reauth: %s' % session['_fresh'])
            #flash(_('Reauthenticated.'), 'success')
            #return redirect('/change_password')

        #flash(_('Password is wrong.'), 'error')
    #return render_template('home/reauth.html', form=form)


#@home.route('/logout')
#@login_required
#def logout():
    #logout_user()
    #flash(_('Logged out'), 'success')
    #return redirect(url_for('home.index'))


#@home.route('/signup', methods=['GET', 'POST'])
#def signup():
    #if current_user.is_authenticated():
        #return redirect(url_for('user.index'))

    #form = SignupForm(next=request.args.get('next'))

    #if form.validate_on_submit():
        #user = User()
        #user = user.create(**(dict(uNam=form.name.data, email=form.email.data, pw=form.password.name)))

        #if login_user(user):
            #return redirect(form.next.data or url_for('user.index'))

    #return render_template('home/signup.html', form=form)


#@home.route('/change_password', methods=['GET', 'POST'])
#def change_password():
    #user = None
    #if current_user.is_authenticated():
        #if not login_fresh():
            #return login_manager.needs_refresh()
        #user = current_user
    #elif 'activation_key' in request.values and 'email' in request.values:
        #activation_key = request.values['activation_key']
        #email = request.values['email']
        #user = User.query.filter_by(activation_key=activation_key) \
                         #.filter_by(email=email).first()

    #if user is None:
        #abort(403)

    #form = ChangePasswordForm(activation_key=user.activation_key)

    #if form.validate_on_submit():
        #user.password = form.password.data
        #user.activation_key = None
        #db.session.add(user)
        #db.session.commit()

        #flash(_("Your password has been changed, please log in again"),
              #"success")
        #return redirect(url_for("home.login"))

    #return render_template("home/change_password.html", form=form)


#@home.route('/reset_password', methods=['GET', 'POST'])
#def reset_password():
    #form = RecoverPasswordForm()

    #if form.validate_on_submit():
        #user = User.query.filter_by(email=form.email.data).first()

        #if user:
            #flash('Please see your email for instructions on '
                  #'how to access your account', 'success')

            #user.activation_key = str(uuid4())
            #db.session.add(user)
            #db.session.commit()

            #url = url_for('home.change_password', email=user.email, activation_key=user.activation_key, _external=True)
            #html = render_template('macros/_reset_password.html', project=current_app.config['PROJECT'], username=user.name, url=url)
            #message = Message(subject='Reset your password in ' + current_app.config['PROJECT'], html=html, recipients=[user.email])
            #mail.send(message)

            #return render_template('home/reset_password.html', form=form)
        #else:
            #flash(_('Sorry, no user found for that email address'), 'error')

    #return render_template('home/reset_password.html', form=form)


#@home.route('/about')
#def about():
    #return render_template('home/footers/about.html', active="about")


#@home.route('/blog')
#def blog():
    #return render_template('home/footers/blog.html', active="blog")


#@home.route('/help')
#def help():
    #return render_template('home/footers/help.html', active="help")


#@home.route('/privacy')
#def privacy():
    #return render_template('home/footers/privacy.html', active="privacy")


#@home.route('/terms')
#def terms():
    #return render_template('home/footers/terms.html', active="terms")
