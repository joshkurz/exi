# -*- coding: utf-8 -*-

import sys
import os
import re
from unittest import TestCase
import flask
from flask import current_app
from flask.testsuite import FlaskTestCase, emits_module_deprecation_warning
import datetime
import random
from exi.helpers import CreateApp
from exi.settings import TestConfig
from exi.db import db

sys.path.pop(0)
sys.path.insert(0, os.getcwd())

class BaseMongoTestCase(TestCase):
    def setUp(self):
        super(BaseMongoTestCase, self).setUp()
        
        app = CreateApp(TestConfig).get_app(__name__)
        app.template_folder = os.path.join(os.path.abspath(__file__ + "/../../"), 'templates')
        
        self.tests_data_yaml_dir = app.config['HOME_PATH'] + 'tests/data/yaml/'
        self.data_dir            = app.config['HOME_PATH'] + 'data/'

        self.config = app.config
        
        #g           = globals.load()
        g = {}
        g['usr']    = {"OID": "50468de92558713d84b03fd7", "at": (-84.163063, 9.980516)}
        g['logger'] = app.logger
        self.g = g
        app.g = g
        self.app = app
        
        self._flush_db()


    def tearDown(self):
        #self._flush_db()
        pass

    def _flush_db(self):
        #Truncate/wipe the test database
        names = [name for name in db.collection_names() \
            if 'system.' not in name]
        [db.drop_collection(name) for name in names]

    def assertEqualDateTimes(self, expected, actual):
        expected = (expected.year, expected.month, expected.day, expected.hour, expected.minute)
        actual = (actual.year, actual.month, actual.day, actual.hour, actual.minute)
        self.assertEqual(expected, actual)
