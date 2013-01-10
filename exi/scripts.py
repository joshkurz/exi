# -*- coding: utf-8 -*-
import re
from flask.ext.script import Command, Option
#from exi.controllers.security import RegistrationKey
from flask_pymongo_security.utils import encrypt_password
from exi.utils.clean_pyc import clean_pyc
from exi.utils.populate import populate_data
from exi.db import db
import datetime

# class ClearActivationKeys(Command):
#     """Clearout inactive ActivationKeys"""

#     option_list = (
#         Option('-t', '--time', dest='hoursBack', default=48),
#     )

#     def run(self, hoursBack, **kwargs):

#         query = db.session.query(RegistrationKey).filter(RegistrationKey.created < (datetime.datetime.now() - datetime.timedelta(hours=hoursBack)))
#         print "Deleting %s keys" % query.count()
#         query.delete(synchronize_session=False)
#         db.session.commit()

class CreateUser(Command):
    """Create a new role"""

    option_list = (
        Option( "--email", "-e", dest="email_address", help="Email"),
        Option( "--password", "-p", dest="password", help="Password"),
        Option( "--roles", "-r", dest="roles", help="Role names"),
    )

    def run( self, email_address, password, roles):
        from exi.models import Role, User
        
        # make sure roles exist
        roles = re.split(r"\s*,\s*", roles)
        for role in roles:
            if not Role().find_one(dict(name=role)):
                print "Role: %s does not exist. Create it first." % role
                return
        
        # does the user already exist?
        if User().find_one(dict(email=email_address)):
            print "Email: %s already exists." % email_address
            return

        pw = encrypt_password(password)
        user = User().create(**dict(email=email_address, password=pw, confirmed_at=datetime.datetime.utcnow()))

        for role in roles:
            if not UserAddRole().run(**dict(email_address=user.email, role_name=role)):
                print "Failed to add role: %s" % role

class CreateRole(Command):
    """Create a new role"""

    option_list = (
        Option( "--description", "-d", dest="desc", help="Description"),
        Option( "--role", "-r", dest="role_name", help="Role name"),
    )

    def run( self, role_name, desc):
        from exi.models import Role, User
        
        role = Role().create(**dict(name=role_name, description=desc))
        if not role:
            print "Failed to create role: %s." % role_name
        else:
            print "Created new role:", role.vNam

class UserRemoveRole(Command):
    """Adds a role to a user"""

    option_list = (
        Option( "--email", "-e", dest="email_address", help="User's email"),
        Option( "--role", "-r", dest="role_name", help="Role name"),
    )

    def run( self, email_address, role_name):
        from exi.models import Role, User
        
        role = Role().find_one(dict(name=role_name))
        if not role:
            print "Role %s does not exit." % role_name
            return
        
        email = email_address.lower().strip()
        user = User().find_one(dict(email=email))
        if not user:
            print "Email %s does not exist." % email_address
            return

        if not user.remove_role(role):
            print "Failed to remove role %s to user with email %s." % (role_name, email_address)
            return

class UserAddRole(Command):
    """Adds a role to a user"""

    option_list = (
        Option( "--email", "-e", dest="email_address", help="User's email"),
        Option( "--role", "-r", dest="role_name", help="Role to add"),
    )

    def run( self, email_address, role_name):
        from exi.models import Role, User
        
        role = Role().find_one(dict(name=role_name))
        if not role:
            print "Role %s does not exit." % role_name
            return
        
        email = email_address.lower().strip()
        user = User().find_one(dict(email=email))
        if not user:
            print "Email %s does not exist." % email_address
            return

        if not user.add_role(role):
            print "Failed to add role %s to user with email %s." % (role_name, email_address)
            return
        
        return True

class ResetDB(Command):
    """Drops all tables and recreates them"""
    def run(self, **kwargs):
        names = [name for name in db.collection_names() \
            if 'system.' not in name]
        [db.drop_collection(name) for name in names]

        populate_data()

class CleanPyc(Command):
    """Removes all *.pyc files from the project folder"""
    def run(self, **kwargs):
        clean_pyc()

class PopulateDB(Command):
    """Fills in predefined data into DB"""
    def run(self, **kwargs):
        populate_data()
