# -*- coding: utf-8 -*-
"""
    flask.ext.security.datastore
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module contains an user datastore classes.

    :copyright: (c) 2012 by Matt Wright.
    :license: MIT, see LICENSE for more details.
"""
"""
Adapted for pymongo usecase.
"""
import time, datetime
from bson import ObjectId
from flask import current_app
from exi.db import db

class Datastore(object):
    #def __init__(self, db):
        #self.db = db

    def commit(self):
        pass

    def put(self, model):
        raise NotImplementedError

    def delete(self, model):
        raise NotImplementedError

class PyMongoDatastore(Datastore):
    def put(self, model):
        model.save()
        return model

    def delete(self, model):
        model.delete()

class PyMongoUserDataStore(Datastore):
    def __init__(self, user_model, role_model):
        #self.db = db
        self.user_model = user_model
        self.role_model = role_model
        
class UserDatastore(object):
    """Abstracted user datastore.

    :param user_model: A user model class definition
    :param role_model: A role model class definition
    """

    def __init__(self, user_model, role_model):
        self.user_model = user_model
        self.role_model = role_model

    def is_active(self):
        return self.user_model.active
    
    def is_authenticated(self):
        """
        Returns `True`.
        """
        return True    
    
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

    def find_user(self, **kwargs):
        """Returns a user matching the provided paramters."""
        raise NotImplementedError

    def find_role(self, **kwargs):
        """Returns a role matching the provided paramters."""
        raise NotImplementedError

    def add_role_to_user(self, user, role):
        """Adds a role tp a user

        :param user: The user to manipulate
        :param role: The role to add to the user
        """
        rv = False
        user, role = self._prepare_role_modify_args(user, role)
        if role not in user.roles:
            rv = True
            user.roles.append(role)
        return rv

    def remove_role_from_user(self, user, role):
        """Removes a role from a user

        :param user: The user to manipulate
        :param role: The role to remove from the user
        """
        rv = False
        user, role = self._prepare_role_modify_args(user, role)
        if role in user.roles:
            rv = True
            user.roles.remove(role)
        return rv

    def toggle_active(self, user):
        """Toggles a user's active status. Always returns True."""
        user.active = not user.active
        return True

    def deactivate_user(self, user):
        """Deactivates a specified user.
        :param user: The user to deactivate
        """
        if not user.active:
            return True
        else:
            if db[self.user_model.colNam].find_and_modify(query={"_id": user.id},
                            update={"$unset": {"active": 1}}):
                user.active = False
                return True
        return False

    def activate_user(self, user):
        """Activates a specified user.
        :param user: The user to activate
        """
        if user.active:
            return True
        else:
            if db[self.user_model.colNam].find_and_modify(query={"_id": user.id}, update={"$set": {"active": True}}):
                user.active = True
                return True
        return False

    def create_role(self, **kwargs):
        """Creates and returns a new role from the given parameters."""

        role = self.role_model(**kwargs)
        #role.set_db(self.db.db)
        return role.save()

    def create_user(self, **kwargs):
        """Creates and returns a new user from the given parameters."""

        user = self.user_model(**self._prepare_create_user_args(**kwargs))
        return self.put(user)

    def delete_user(self, user):
        """Delete the specified user

        :param user: The user to delete
        """
        self.user_model().delete(dict(_id=user.id))


        
class PyMongoUserDatastore(PyMongoDatastore, UserDatastore):
    """A PyMongo datastore implementation for Flask-Security that assumes
    the use of the Flask-MongoEngine extension.
    """
    def __init__(self, user_model, role_model):
        self.user_model = user_model
        self.role_model = role_model
        
        PyMongoDatastore.__init__(self)
        UserDatastore.__init__(self, user_model, role_model)

    def create_user(self, **kwargs):
        """Creates and returns a new user from the given parameters."""

        
        user = self.user_model(**self._prepare_create_user_args(**kwargs)) 
        user.save()
        return user

    def find_user(self, **kwargs):
        # map to correct params
        if 'id' in kwargs:
            new_kwargs = dict(_id=ObjectId(kwargs['id']))
            userDict = self.user_model().find_one(new_kwargs)
        else:
            userDict = self.user_model().find_one(kwargs)
            
        if userDict:
            # handle replacing empty/false fields not persisted in User
            user = self.user_model(**userDict)
            user.active = 'active' in userDict
            return user
        else:
            # TODO: Handle error
            pass

    def find_role(self, role):
        return self.role_model().find_one(dict(name=role))
