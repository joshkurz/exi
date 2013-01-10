# -*- coding: utf-8 -*-
from exi.home import TestForm
#from .utils import get_url, get_post_login_redirect, do_flash, get_message, login_user, logout_user, url_for_security as url_for

from flask_pymongo_security.utils import url_for_security as url_for

#from flask_pymongo_security.forms import LoginForm, ConfirmRegisterForm, RegisterForm, ForgotPasswordForm, ResetPasswordForm, SendConfirmationForm, PasswordlessLoginForm
from flask_pymongo_security.forms import LoginForm


def common_context():
    return {'my_email': 'larry@eitel.com'
            }

def navigation():
    main_page = {'name': 'Main',
                 'url': '/',
                 #'url': url_for('home.index'),
                 }

    return {'navigation': (main_page)}


def common_forms():
    return {'login_form': LoginForm()}
