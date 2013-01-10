# -*- coding: utf-8 -*-
import sys, os

sys.path.pop(0)
sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.abspath(__file__ + "/../../../../"))
# a hack until I make flask-pymongo-security and external package
sys.path.insert(0, os.path.join(os.path.abspath(__file__ + "/../../../../"), 'flask-pymongo-security'))

from unittest import TestCase
from exi.tests.security.test_app.pymongo_app import create_app

class SecurityTest(TestCase):

    APP_KWARGS = {
        'register_blueprint': True,
    }
    AUTH_CONFIG = None

    def setUp(self):
        super(SecurityTest, self).setUp()

        app_kwargs = self.APP_KWARGS
        app = self._create_app(self.AUTH_CONFIG or {}, **app_kwargs)
        app.debug = False
        app.config['TESTING'] = True

        self.app = app
        self.client = app.test_client()

    def _create_app(self, auth_config, **kwargs):
        return create_app(auth_config, **kwargs)

    def _get(self, route, content_type=None, follow_redirects=None, headers=None):
        return self.client.get(route, follow_redirects=follow_redirects,
                content_type=content_type or 'text/html',
                headers=headers)

    def _post(self, route, data=None, content_type=None, follow_redirects=True, headers=None):
        return self.client.post(route, data=data,
                follow_redirects=follow_redirects,
                content_type=content_type or 'application/x-www-form-urlencoded',
                headers=headers)

    def register(self, email, password='password'):
        data = dict(email=email, password=password)
        return self.client.post('/register', data=data, follow_redirects=True)

    def authenticate(self, email="matt@lp.com", password="password", endpoint=None, **kwargs):
        data = dict(email=email, password=password, remember='y')
        r = self._post(endpoint or '/login', data=data, **kwargs)
        return r

    def json_authenticate(self, email="matt@lp.com", password="password", endpoint=None):
        data = """
{
    "email": "%s",
    "password": "%s"
}
"""
        return self._post(endpoint or '/login',
                          content_type="application/json",
                          data=data % (email, password))

    def logout(self, endpoint=None):
        return self._get(endpoint or '/logout', follow_redirects=True)

    def assertIsHomePage(self, data):
        self.assertIn('Home Page', data)

    def assertIn(self, member, container, msg=None):
        if hasattr(TestCase, 'assertIn'):
            return TestCase.assertIn(self, member, container, msg)

        return self.assertTrue(member in container)

    def assertNotIn(self, member, container, msg=None):
        if hasattr(TestCase, 'assertNotIn'):
            return TestCase.assertNotIn(self, member, container, msg)

        return self.assertFalse(member in container)

    def assertIsNotNone(self, obj, msg=None):
        if hasattr(TestCase, 'assertIsNotNone'):
            return TestCase.assertIsNotNone(self, obj, msg)

        return self.assertTrue(obj is not None)

    def get_message(self, key, **kwargs):
        return self.app.config['SECURITY_MSG_' + key][0] % kwargs
