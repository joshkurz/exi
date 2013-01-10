# -*- coding: utf-8 -*-
from flask import Markup
from flask.ext.wtf import Form, TextField, Required, Length, EqualTo, PasswordField, HiddenField, BooleanField, SubmitField
from flask.ext.wtf.html5 import EmailField
from wtforms.validators import Email

# from app import User

PASSWORD_LEN_MIN = 6
PASSWORD_LEN_MAX = 32
USERNAME_LEN_MIN = 6
USERNAME_LEN_MAX = 64

class TestForm(Form):
    agree = BooleanField(u'Agree to the ' + 
        Markup('<a target="blank" href="/terms">Terms of Servic</a>'), [Required()])
    submit = SubmitField('Sign up')
    
#class LoginForm(Form):
    #email = TextField('Login', validators=[Required(), Email()])
    #password = PasswordField('Password', validators=[Required()])

#class SignupForm(Form):
    #next = HiddenField()
    #email = EmailField(u'Email', [Required(), Email()],
            #description=u"What's your email address?")
    #password = PasswordField(u'Password', [Required(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)],
            #description=u'%s characters or more! Be tricky.' % PASSWORD_LEN_MIN)
    #name = TextField(u'Choose your username', [Required(), Length(USERNAME_LEN_MIN, USERNAME_LEN_MAX)],
            #description=u"Don't worry. you can change it later.")
    #agree = BooleanField(u'Agree to the ' + 
        #Markup('<a target="blank" href="/terms">Terms of Servic</a>'), [Required()])
    #submit = SubmitField('Sign up')

    #def validate_name(self, field):
        #pass
        ##if User.query.filter_by(name=field.data).first() is not None:
            ##raise ValidationError(u'This username is taken')

    #def validate_email(self, field):
        #pass
        ##if User.query.filter_by(email=field.data).first() is not None:
            ##raise ValidationError(u'This email is taken')


#class RecoverPasswordForm(Form):
    #email = EmailField(u'Your email', [Email()])
    #submit = SubmitField('Send instructions')


#class ChangePasswordForm(Form):
    #activation_key = HiddenField()
    #password = PasswordField(u'Password', [Required()])
    #password_again = PasswordField(u'Password again', [EqualTo('password', message="Passwords don't match")]) 
    #submit = SubmitField('Save')


#class ReauthForm(Form):
    #next = HiddenField()
    #password = PasswordField(u'Password', [Required(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)])
    #submit = SubmitField('Reauthenticate')
