# -*- coding: utf-8 -*-
"""
    flask.ext.security.utils
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Flask-Security utils module

    :copyright: (c) 2012 by Matt Wright.
    :license: MIT, see LICENSE for more details.
"""

import base64
import blinker
import functools
import hashlib
import hmac
from contextlib import contextmanager
from datetime import datetime, timedelta

from flask import url_for, flash, current_app, request, session, render_template
from flask.ext.login import login_user as _login_user, \
     logout_user as _logout_user
from flask.ext.mail import Message
from flask.ext.principal import Identity, AnonymousIdentity, identity_changed
from itsdangerous import BadSignature, SignatureExpired
from werkzeug.local import LocalProxy

from .signals import user_registered, user_confirmed, \
    confirm_instructions_sent, login_instructions_sent, \
    password_reset, reset_password_instructions_sent

# Convenient references
_security = LocalProxy(lambda: current_app.extensions['security'])

_datastore = LocalProxy(lambda: _security.datastore)

_pwd_context = LocalProxy(lambda: _security.pwd_context)


def login_user(user, remember=True):
    """Performs the login and sends the appropriate signal."""

    if not _login_user(user, remember):
        return False

    if _security.trackable:
        old_current_login, new_current_login = user.current_login_at, datetime.utcnow()
        remote_addr = request.remote_addr or 'untrackable'
        old_current_ip, new_current_ip = user.current_login_ip, remote_addr

        user.last_login_at = old_current_login or new_current_login
        user.current_login_at = new_current_login
        user.last_login_ip = old_current_ip or new_current_ip
        user.current_login_ip = new_current_ip
        user.login_count = user.login_count + 1 if user.login_count else 1

        # _datastore.put(user)
        user.save()

    identity_changed.send(current_app._get_current_object(),
                          identity=Identity(user.id))
    return True


def logout_user():
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)
    identity_changed.send(current_app._get_current_object(),
                          identity=AnonymousIdentity())
    _logout_user()


def get_hmac(password):
    if _security.password_hash == 'plaintext':
        return password

    if _security.password_salt is None:
        raise RuntimeError('The configuration value `SECURITY_PASSWORD_SALT` '
            'must not be None when the value of `SECURITY_PASSWORD_HASH` is '
            'set to "%s"' % _security.password_hash)

    h = hmac.new(_security.password_salt, password, hashlib.sha512)
    return base64.b64encode(h.digest())


def verify_password(password, password_hash):
    return _pwd_context.verify(get_hmac(password), password_hash)


def verify_and_update_password(password, user):
    verified, new_password = _pwd_context.verify_and_update(get_hmac(password), user.password)
    if verified and new_password:
        #user.password = new_password
        user.update_password(new_password)
        #_datastore.put(user)
    return verified


def encrypt_password(password):
    return _pwd_context.encrypt(get_hmac(password))


def md5(data):
    return hashlib.md5(data).hexdigest()


def do_flash(message, category=None):
    """Flash a message depending on if the `FLASH_MESSAGES` configuration
    value is set.

    :param message: The flash message
    :param category: The flash message category
    """
    if config_value('FLASH_MESSAGES'):
        flash(message, category)


def get_url(endpoint_or_url):
    """Returns a URL if a valid endpoint is found. Otherwise, returns the
    provided value.

    :param endpoint_or_url: The endpoint name or URL to default to
    """
    try:
        return url_for(endpoint_or_url)
    except:
        return endpoint_or_url


def get_security_endpoint_name(endpoint):
    return '%s.%s' % (_security.blueprint_name, endpoint)


def url_for_security(endpoint, **values):
    """Return a URL for the security blueprint

    :param endpoint: the endpoint of the URL (name of the function)
    :param values: the variable arguments of the URL rule
    :param _external: if set to `True`, an absolute URL is generated. Server
      address can be changed via `SERVER_NAME` configuration variable which
      defaults to `localhost`.
    :param _anchor: if provided this is added as anchor to the URL.
    :param _method: if provided this explicitly specifies an HTTP method.
    """
    endpoint = get_security_endpoint_name(endpoint)
    return url_for(endpoint, **values)


def get_post_login_redirect():
    """Returns the URL to redirect to after a user logs in successfully."""
    return (get_url(request.args.get('next')) or
            get_url(request.form.get('next')) or
            find_redirect('SECURITY_POST_LOGIN_VIEW'))


def find_redirect(key):
    """Returns the URL to redirect to after a user logs in successfully.

    :param key: The session or application configuration key to search for
    """
    rv = (get_url(session.pop(key.lower(), None)) or
          get_url(current_app.config[key.upper()] or None) or '/')
    return rv


def get_config(app):
    """Conveniently get the security configuration for the specified
    application without the annoying 'SECURITY_' prefix.

    :param app: The application to inspect
    """
    items = app.config.items()
    prefix = 'SECURITY_'

    def strip_prefix(tup):
        return (tup[0].replace('SECURITY_', ''), tup[1])

    return dict([strip_prefix(i) for i in items if i[0].startswith(prefix)])


def get_message(key, **kwargs):
    rv = config_value('MSG_' + key)
    return rv[0] % kwargs, rv[1]


def config_value(key, app=None, default=None):
    """Get a Flask-Security configuration value.

    :param key: The configuration key without the prefix `SECURITY_`
    :param app: An optional specific application to inspect. Defaults to Flask's
                `current_app`
    :param default: An optional default value if the value is not set
    """
    app = app or current_app
    return get_config(app).get(key.upper(), default)


def get_max_age(key, app=None):
    now = datetime.utcnow()
    expires = now + get_within_delta(key + '_WITHIN', app)
    return (expires - now).total_seconds()


def get_within_delta(key, app=None):
    """Get a timedelta object from the application configuration following
    the internal convention of::

        <Amount of Units> <Type of Units>

    Examples of valid config values::

        5 days
        10 minutes

    :param key: The config value key without the 'SECURITY_' prefix
    :param app: Optional application to inspect. Defaults to Flask's
                `current_app`
    """
    txt = config_value(key, app=app)
    values = txt.split()
    return timedelta(**{values[1]: int(values[0])})


def send_mail(subject, recipient, template, **context):
    """Send an email via the Flask-Mail extension.

    :param subject: Email subject
    :param recipient: Email recipient
    :param template: The name of the email template
    :param context: The context to render the template with
    """

    context.setdefault('security', _security)
    context.update(_security._run_ctx_processor('mail'))

    msg = Message(subject,
                  sender=_security.email_sender,
                  recipients=[recipient])

    ctx = ('security/email', template)
    msg.body = render_template('%s/%s.txt' % ctx, **context)
    msg.html = render_template('%s/%s.html' % ctx, **context)

    if _security._send_mail_task:
        _security._send_mail_task(msg)
        return

    mail = current_app.extensions.get('mail')
    mail.send(msg)


def get_token_status(token, serializer, max_age=None):
    serializer = getattr(_security, serializer + '_serializer')
    max_age = get_max_age(max_age)
    user, data = None, None
    expired, invalid = False, False

    try:
        data = serializer.loads(token, max_age=max_age)
    except SignatureExpired:
        d, data = serializer.loads_unsafe(token)
        expired = True
    except BadSignature:
        invalid = True

    if data:
        user = _datastore.find_user(id=data[0])

    expired = expired and (user is not None)
    return expired, invalid, user


@contextmanager
def capture_passwordless_login_requests():
    login_requests = []

    def _on(data, app):
        login_requests.append(data)

    login_instructions_sent.connect(_on)

    try:
        yield login_requests
    finally:
        login_instructions_sent.disconnect(_on)


@contextmanager
def capture_registrations():
    """Testing utility for capturing registrations.

    :param confirmation_sent_at: An optional datetime object to set the
                                 user's `confirmation_sent_at` to
    """
    registrations = []

    def _on(data, app):
        registrations.append(data)

    user_registered.connect(_on)

    try:
        yield registrations
    finally:
        user_registered.disconnect(_on)


@contextmanager
def capture_reset_password_requests(reset_password_sent_at=None):
    """Testing utility for capturing password reset requests.

    :param reset_password_sent_at: An optional datetime object to set the
                                   user's `reset_password_sent_at` to
    """
    reset_requests = []

    def _on(request, app):
        reset_requests.append(request)

    reset_password_instructions_sent.connect(_on)

    try:
        yield reset_requests
    finally:
        reset_password_instructions_sent.disconnect(_on)


class CaptureSignals(object):
    """Testing utility for capturing blinker signals.

    Context manager which mocks out selected signals and registers which are `sent` on and what
    arguments were sent. Instantiate with a list of blinker `NamedSignals` to patch. Each signal
    has it's `send` mocked out.
    """
    def __init__(self, signals):
        """Patch all given signals and make them available as attributes.

        :param signals: list of signals
        """
        self._records = {}
        self._receivers = {}
        for signal in signals:
            self._records[signal] = []
            self._receivers[signal] = functools.partial(self._record, signal)

    def __getitem__(self, signal):
        """All captured signals are available via `ctxt[signal]`.
        """
        if isinstance(signal, blinker.base.NamedSignal):
            return self._records[signal]
        else:
            super(CaptureSignals, self).__setitem__(signal)

    def _record(self, signal, *args, **kwargs):
        self._records[signal].append((args, kwargs))

    def __enter__(self):
        for signal, receiver in self._receivers.iteritems():
            signal.connect(receiver)
        return self

    def __exit__(self, type, value, traceback):
        for signal, receiver in self._receivers.iteritems():
            signal.disconnect(receiver)

    def signals_sent(self):
        """Return a set of the signals sent.
        :rtype: list of blinker `NamedSignals`.
        """
        return set([signal for signal, _ in self._records.iteritems() if self._records[signal]])


def capture_signals():
    """Factory method that creates a `CaptureSignals` with all the flask_security signals."""
    return CaptureSignals([user_registered, user_confirmed,
                           confirm_instructions_sent, login_instructions_sent,
                           password_reset, reset_password_instructions_sent])


