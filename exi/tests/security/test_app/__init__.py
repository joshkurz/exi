# -*- coding: utf-8 -*-
import os
from datetime import datetime
from flask import Flask, render_template, current_app
from flask.ext.mail import Mail
from flask_pymongo_security import login_required, roles_required, roles_accepted
from flask_pymongo_security.decorators import http_auth_required, auth_token_required
from flask_pymongo_security.utils import encrypt_password
from werkzeug.local import LocalProxy
from exi.settings import TestConfig

ds = LocalProxy(lambda: current_app.extensions['security'].datastore)

def create_app(config):
    app = Flask(__name__)
    app.debug = True
    app.config['SECRET_KEY'] = 'secret'

    app.config.from_object(TestConfig)
    app.config.from_envvar('PROJECT_SETTINGS', silent=True)
    app.config.from_pyfile('local_settings.py', silent=True)

    for key, value in config.items():
        app.config[key] = value

    app.template_folder = os.path.join(os.path.abspath(__file__ + "/../../../../"), 'templates')
    
    mail = Mail(app)
    app.extensions['mail'] = mail

    @app.route('/')
    def index():
        return render_template('index.html', content='Home Page')

    @app.route('/profile')
    @login_required
    def profile():
        return render_template('index.html', content='Profile Page')

    @app.route('/post_login')
    @login_required
    def post_login():
        return render_template('index.html', content='Post Login')

    @app.route('/http')
    @http_auth_required
    def http():
        return 'HTTP Authentication'

    @app.route('/http_custom_realm')
    @http_auth_required('My Realm')
    def http_custom_realm():
        return render_template('index.html', content='HTTP Authentication')

    @app.route('/token')
    @auth_token_required
    def token():
        return render_template('index.html', content='Token Authentication')

    @app.route('/post_logout')
    def post_logout():
        return render_template('index.html', content='Post Logout')

    @app.route('/post_register')
    def post_register():
        return render_template('index.html', content='Post Register')

    @app.route('/admin')
    @roles_required('admin')
    def admin():
        return render_template('index.html', content='Admin Page')

    @app.route('/admin_and_editor')
    @roles_required('admin', 'editor')
    def admin_and_editor():
        return render_template('index.html', content='Admin and Editor Page')

    @app.route('/admin_or_editor')
    @roles_accepted('admin', 'editor')
    def admin_or_editor():
        return render_template('index.html', content='Admin or Editor Page')

    @app.route('/unauthorized')
    def unauthorized():
        return render_template('unauthorized.html')

    @app.route('/coverage/add_role_to_user')
    def add_role_to_user():
        u = ds.find_user(email='joe@lp.com')
        r = ds.find_role('admin')
        ds.add_role_to_user(u, r)
        return 'success'

    @app.route('/coverage/remove_role_from_user')
    def remove_role_from_user():
        u = ds.find_user(email='matt@lp.com')
        ds.remove_role_from_user(u, 'admin')
        return 'success'

    @app.route('/coverage/deactivate_user')
    def deactivate_user():
        u = ds.find_user(email='matt@lp.com')
        ds.deactivate_user(u)
        return 'success'

    @app.route('/coverage/activate_user')
    def activate_user():
        u = ds.find_user(email='tiya@lp.com')
        ds.activate_user(u)
        return 'success'

    @app.route('/coverage/invalid_role')
    def invalid_role():
        return 'success' if ds.find_role('bogus') is None else 'failure'

    def _get_imported_stuff_by_path(path):
        mo_pa = path.split('.')
        module_name = '.'.join(mo_pa[:-1])
        objNam = mo_pa[-1]
        module = __import__(module_name, fromlist=[objNam])

        return module, objNam

    def _bind_extensions(app):
        for ext_path in app.config.get('EXTENSIONS', []):
            module, e_name = _get_imported_stuff_by_path(ext_path)
            if not hasattr(module, e_name):
                raise NoExtensionException('No {e_name} extension found'.format(e_name=e_name))
            ext = getattr(module, e_name)
            if getattr(ext, 'init_app', False):
                ext.init_app(app)
            else:
                ext(app)

    def _register_context_processors(self):
        for processor_path in app.config.get('CONTEXT_PROCESSORS', []):
            module, p_name = _get_imported_stuff_by_path(processor_path)
            if hasattr(module, p_name):
                app.context_processor(getattr(module, p_name))
            else:
                raise NoContextProcessorException('No {cp_name} context processor found'.format(cp_name=p_name))

    def _register_blueprints(self):
        for blueprint_path in app.config.get('BLUEPRINTS', []):
            module, b_name = _get_imported_stuff_by_path(blueprint_path)
            if hasattr(module, b_name):
                app.register_blueprint(getattr(module, b_name))
            else:
                raise NoBlueprintException('No {bp_name} blueprint found'.format(bp_name=b_name))

    _bind_extensions(app)
    _register_blueprints(app)
    _register_context_processors(app)

    return app






def create_roles():
    for role in ('admin', 'editor', 'author'):
        ds.create_role(name=role)
    ds.commit()

def create_users(count=None):
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

def populate_data(user_count=None):
    create_roles()
    create_users(user_count)

def add_context_processors(s):
    @s.context_processor
    def for_all():
        return dict()

    @s.forgot_password_context_processor
    def forgot_password():
        return dict()

    @s.login_context_processor
    def login():
        return dict()

    @s.register_context_processor
    def register():
        return dict()

    @s.reset_password_context_processor
    def reset_password():
        return dict()

    @s.send_confirmation_context_processor
    def send_confirmation():
        return dict()

    @s.send_login_context_processor
    def send_login():
        return dict()

    @s.mail_context_processor
    def mail():
        return dict()
