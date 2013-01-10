# -*- coding: utf-8 -*-

import sys, os
# a hack until I make flask-pymongo-security and external package
sys.path.insert(0, os.path.join(os.path.abspath(__file__ + "/../../../"), 'flask-pymongo-security'))

from exi.db import db
from d import D
from cnt import Prs
from schematics.types import IntType, StringType, DateTimeType, EmailType, BooleanType
from schematics.types.compound import ListType, ModelType

from flask_pymongo_security.core import UserMixin, RoleMixin

class Role(D, RoleMixin):
    colNam = 'roles'

    name        = StringType(required=True,max_length=80)
    description = StringType(max_length=255)

    meta   = {
        'colNam': 'roles',
        '_c': 'Role',
        }

    def create(self, **kwargs):
        """Creates and returns a new role from the given parameters."""
        return Role(**kwargs)

    @staticmethod
    def drop_collection():
        pass

    @property
    def vNam(self):
        return self.name + ': ' + self.description
        

class User(Prs, UserMixin):
    colNam = 'cnts'
    
    email            = EmailType(max_length=255)
    password         = StringType(required=True, max_length=255)
    last_login_at    = DateTimeType()
    current_login_at = DateTimeType()
    last_login_ip    = StringType(max_length=100)
    current_login_ip = StringType(max_length=100)
    login_count      = IntType()
    active           = BooleanType(default=True)
    confirmed_at     = DateTimeType()
    roles            = ListType(ModelType(Role))

    meta   = {
        'colNam': 'cnts',
        '_c': 'User',
        }

    @staticmethod
    def drop_collection():
        pass

    #@classmethod
    #def create(self, uNam, email, pw, email_verified=True):
        #now = datetime.datetime.utcnow()

        # Normalize the address by lowercasing the domain part of the email
        # address.
        #try:
            #email_name, domain_part = email.strip().split('@', 1)
        #except ValueError:
            #pass
        #else:
            #email = '@'.join([email_name.lower(), domain_part.lower()])

        #user = User(uNam=uNam, email=email, joined=now)

        #user.save()
        #return user
        

    @classmethod
    def create(self, **kwargs):
        """Creates and returns a new user from the given parameters."""

        # Normalize the address by lowercasing the domain part of the email
        # address.
        try:
            email_name, domain_part = kwargs['email'].strip().split('@', 1)
        except ValueError:
            pass
        else:
            kwargs['email'] = '@'.join([email_name.lower(), domain_part.lower()])
        
        user = User(**kwargs)
        user.save()
        return user
        
    def _prepare_role_modify_args(self, user, role):
        if isinstance(user, basestring):
            user = self.find_user(email=user)
        if isinstance(role, basestring):
            role = self.find_role(role)
        return user, role

    def _prepare_create_user_args(self, **kwargs):
        kwargs.setdefault('active', True)
        roles = kwargs.get('roles', [])
        for i, role in enumerate(roles):
            rn = role.name if isinstance(role, self.role_model) else role
            # see if the role exists
            roles[i] = self.find_role(rn)
        kwargs['roles'] = roles
        return kwargs
    

    def is_admin(self):
        return True
        
    def add_role(self, role):
        """Adds a role tp a user
        :param role: The role to add to the user
        """
        if role.name not in [r.name for r in self.roles]:
            return db[self.colNam].find_and_modify(query=dict(_id=self.id), update={'$push': {'roles': role.to_python()}})

    def remove_role(self, role):
        """Removes a role from a user
        :param role: The role to remove from the user
        """
        if role.name in [r.name for r in self.roles]:
            remaining_if_any_roles = [r.to_python() for r in self.roles if not r.name == role.name]
            if remaining_if_any_roles:
                return db[self.colNam].find_and_modify(query=dict(_id=self.id), update={'$set': {'roles': remaining_if_any_roles}})
            else:
                return db[self.colNam].find_and_modify(query=dict(_id=self.id), update={'$unset': {'roles': 1}})

    def toggle_active(self, user):
        """Toggles a user's active status. Always returns True."""
        user.active = not user.active
        return True

    def deactivate_user(self, user):
        """Deactivates a specified user. Returns `True` if a change was made.

        :param user: The user to deactivate
        """
        if user.active:
            user.active = False
            return True
        return False

    def activate_user(self, user):
        """Activates a specified user. Returns `True` if a change was made.

        :param user: The user to activate
        """
        if not user.active:
            user.active = True
            return True
        return False

    def create_role(self, **kwargs):
        """Creates and returns a new role from the given parameters."""

        role = self.role_model(**kwargs)
        return self.put(role)

    def create_user(self, **kwargs):
        """Creates and returns a new user from the given parameters."""

        user = self.user_model(**self._prepare_create_user_args(**kwargs))
        return self.put(user)

    def delete_user(self, user):
        """Delete the specified user

        :param user: The user to delete
        """
        self.delete(user)

    def update_password(self, password):
        return db[self.colNam].find_and_modify(query={"_id": self.id}, update={"$set": {"password": password}})

    def set_confirmed_at(self, dt):
        return db[self.colNam].find_and_modify(query={"_id": self.id}, update={"$set": {"confirmed_at": dt}})

    def save(self):
        super(User, self).save()
        # We do not save empty values but in the case of User, security expects to see this as part of authentification
        if not self.confirmed_at:
            db[self.colNam].find_and_modify(query={"_id": self.id},
                update={"$set": {"confirmed_at": None}})            

    @property
    def vNam(self):
        return self.email
        