from flask import current_app
from d import D
from schematics.types import IntType, StringType, FloatType, DateTimeType, EmailType, URLType, BooleanType
from schematics.types.compound import ListType, ModelType
from ext import db
from schematics.types.mongo import ObjectIdType
from bson import ObjectId
from embed import Email, Note, Tel, Im
from models import Role
from mixins import DMixin
from random import randint, random, Random
import time, hashlib, datetime
from utils.utils import get_hexdigest
#from flask.ext.principal import Principal, Permission, RoleNeed, identity_changed, AnonymousIdentity


class Cnt(D, DMixin):
    '''
    Google Contacts API: https://developers.google.com/google-apps/contacts/v3/
    '''
    code        = StringType(description='')

    # langs       = ListType(ModelType(Lang), description='Languages associated with this contact.')

    meta   = {
        'collNam': 'cnts',
        '_c': 'Cnt',
        }
class Cmp(Cnt):
    '''https://developers.google.com/gdata/docs/2.0/elements#gdOrganization'''
    cNam = StringType(required=True, description='')
    cNamS = StringType(required=True, description='Abbreviation or Acronym')
    symbol = StringType(description='')

    meta = {
        'colNam': 'cnts',
        '_c': 'Cmp',
        }

class Prs(Cnt):
    '''https://developers.google.com/gdata/docs/2.0/elements#gdName'''

    # namePrefix
    prefix    = StringType(description='Examples: Mr, Mrs, Ms, etc')
    
    # givenName
    fNam      = StringType()
    
    # additionalName
    fNam2     = StringType()
    
    # givenName
    lNam      = StringType()
    lNam2     = StringType()
    
    # nameSuffix
    suffix    = StringType(description='Examples: MD, PHD, Jr, Sr, etc')
    gen       = StringType(choices=['m','f'], description='Gender')
    rBy       = ObjectIdType(description='User that referred or registered this user.')
    
    meta      = {
        'colNam': 'cnts',
        '_c'        : 'Prs',
        }
        
    #def vNam(self, prefix='', fNam='', fNam2='', lNam='', lNam2='', suffix='', **kwargs):
    @property
    def vNam(self):
        s = ''
        fNamS = ''
        fNamS += self.prefix + ' ' if self.prefix else ''
        fNamS += self.fNam + ' ' if self.fNam else ''
        fNamS += self.fNam2 + ' ' if self.fNam2 else ''
        fNamS = fNamS[:-1] if fNamS else ''

        lNamS = ''
        lNamS += self.lNam + ' ' if self.lNam else ''
        lNamS += self.lNam2 + ' ' if self.lNam2 else ''
        lNamS += self.suffix + ' ' if self.suffix else ''
        lNamS = lNamS[:-1] if lNamS else ''

        if lNamS:
            s += lNamS
            if fNamS:
                s += ', ' + fNamS
        elif fNamS:
            s += fNamS
        return s



righthand = '23456qwertasdfgzxcvbQWERTASDFGZXCVB'
lefthand = '789yuiophjknmYUIPHJKLNM'
allchars = righthand + lefthand
def genPw(length=8):
    '''generate password'''
    rng = Random()
    chars = []
    for i in range(0,length):
        chars.append( rng.choice(allchars))

    return ''.join( chars)
class Usr(Prs):
    root   = StringType(description='a=Admin, m=Moderator')
    uNam   = StringType(required=True, description='')
    pw     = StringType(description='Password Hash', max_length=128)

    email = StringType(description='Email.')
    emailActKey = StringType(description='Email activation key.')
    isEmailActivated = BooleanType()
    pwRstOn  = DateTimeType(description='Datetime reset.')
    pwRstTkn = StringType(description='Password reset token.')

    joined   = DateTimeType(description='DateTime when user joined the site.')
    confirmed   = DateTimeType(description='DateTime when user confirmed via email.')
    lvOn   = DateTimeType(description='DateTime when user last viewed the site.')

    roles = ListType(StringType())
    
    meta   = {
        'colNam': 'cnts',
        '_c': 'Usr',
        }

    def is_authenticated(self):
        return self.id
        
    def is_anonymous(self):
        return not self.id
    
    def get_id(self):
        return self.id

    def is_active(self):
        return True

    def checkPw(self, rawPw):
        """Checks the user's password against a provided password - always use
        this rather than directly comparing to
        :attr:`~mongoengine.django.auth.User.password` as the password is
        hashed before storage.
        """
        algo, salt, hash = self.pw.split('$')
        return hash == get_hexdigest(algo, salt, rawPw)

    @classmethod
    def getByEmail(cls, email):
        doc = cls.find_one(query=dict(email=email))
        if doc:
            usr = Usr(**doc)
            return usr
    
    @classmethod
    def getById(cls, id):
        doc = cls.find_one(query=dict(_id=id))
        if doc:
            usr = Usr(**doc)
            return usr

    def mark_email_for_activation(self):
        self.isEmailActivated = False
        self.emailActKey = sha_constructor(str(time.time()) + str( randint( 1,1000000))).hexdigest()
    
    def gen_pwRstTkn(self):
        '''generate password reset token'''
        self.pwRstTkn = hashlib.sha1( "%s-%s-%d" % ( str(self.id), str(time.time()), random())).hexdigest()
        self.save()
        return self.pwRstTkn

    def set_pw(self, rawPw):
        """Sets the user's password - always use this rather than using directly
        as the password is hashed before storage.
        """
        algo = 'sha1'
        salt = get_hexdigest(algo, str(random()), str(random()))[:5]
        hash = get_hexdigest(algo, salt, rawPw)
        self.pw = '%s$%s$%s' % (algo, salt, hash)
        self.save()
        return self

    @property
    def vNam(self):
        return self.uNam

# class Datastore(object):
#     def __init__(self, db):
#         self.db = db
        
#     def commit(self):
#         pass

#     def put(self, model):
#         raise NotImplementedError

#     def delete(self, model):
#         raise NotImplementedError

# class PyMongoDatastore(Datastore):
#     def put(self, model):
#         model.save()
#         return model

#     def delete(self, model):
#         model.delete()

# class PyMongoUserDataStore(Datastore):
#     def __init__(self, user_model, role_model):
#         self.db = db
#         self.user_model = user_model
#         self.role_model = role_model
        
class User(object):
    @classmethod
    def create(self, uNam, email, pw, email_verified=True):
        now = datetime.datetime.utcnow()

        # Normalize the address by lowercasing the domain part of the email
        # address.
        try:
            email_name, domain_part = email.strip().split('@', 1)
        except ValueError:
            pass
        else:
            email = '@'.join([email_name.lower(), domain_part.lower()])

        user = User(uNam=uNam, email=email, joined=now)

        if not pw:
            pw = genPw()
        user.set_pw(pw)

        if( not email_verified):
            user.mark_email_for_activation()
        else:
            user.isEmailActivated = True


        user.roles = ['admin']

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
    
    @staticmethod
    def find_user(self, **kwargs):
        """Returns a user matching the provided paramters."""
        user = db[Usr.meta['colNam']].find_one(query=kwargs)
        if user:
            # user = User(**doc)
            return user

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

# class UserDatastore(object):
#     """Abstracted user datastore.

#     :param user_model: A user model class definition
#     :param role_model: A role model class definition
#     """

#     meta = {'colNam': Usr.meta['colNam']}
    
#     def __init__(self, user_model, role_model):
#         self.user_model = user_model
#         self.role_model = role_model

#     def _prepare_role_modify_args(self, user, role):
#         if isinstance(user, basestring):
#             user = self.find_user(email=user)
#         if isinstance(role, basestring):
#             role = self.find_role(role)
#         return user, role

#     def _prepare_create_user_args(self, **kwargs):
#         kwargs.setdefault('active', True)
#         roles = kwargs.get('roles', [])
#         for i, role in enumerate(roles):
#             rn = role.name if isinstance(role, self.role_model) else role
#             # see if the role exists
#             roles[i] = self.find_role(rn)
#         kwargs['roles'] = roles
#         return kwargs

#     def find_user(self, **kwargs):
#         """Returns a user matching the provided paramters."""
#         raise NotImplementedError

#     def find_role(self, **kwargs):
#         """Returns a role matching the provided paramters."""
#         raise NotImplementedError

#     def add_role_to_user(self, user, role):
#         """Adds a role tp a user

#         :param user: The user to manipulate
#         :param role: The role to add to the user
#         """
#         rv = False
#         user, role = self._prepare_role_modify_args(user, role)
#         if role not in user.roles:
#             rv = True
#             user.roles.append(role)
#         return rv

#     def remove_role_from_user(self, user, role):
#         """Removes a role from a user

#         :param user: The user to manipulate
#         :param role: The role to remove from the user
#         """
#         rv = False
#         user, role = self._prepare_role_modify_args(user, role)
#         if role in user.roles:
#             rv = True
#             user.roles.remove(role)
#         return rv

#     def toggle_active(self, user):
#         """Toggles a user's active status. Always returns True."""
#         user.active = not user.active
#         return True

#     def deactivate_user(self, user):
#         """Deactivates a specified user. Returns `True` if a change was made.

#         :param user: The user to deactivate
#         """
#         if user.active:
#             user.active = False
#             return True
#         return False

#     def activate_user(self, user):
#         """Activates a specified user. Returns `True` if a change was made.

#         :param user: The user to activate
#         """
#         if not user.active:
#             user.active = True
#             return True
#         return False

#     def create_role(self, **kwargs):
#         """Creates and returns a new role from the given parameters."""

#         role = self.role_model(**kwargs)
#         return self.put(role)

#     def create_user(self, **kwargs):
#         """Creates and returns a new user from the given parameters."""
#         uNam = kwargs['email']
#         email = kwargs['email']
#         pw = kwargs['password']
        
#         now = datetime.datetime.utcnow()

#         # Normalize the address by lowercasing the domain part of the email
#         # address.
#         try:
#             email_name, domain_part = email.strip().split('@', 1)
#         except ValueError:
#             pass
#         else:
#             email = '@'.join([email_name.lower(), domain_part.lower()])

#         usr = Usr(uNam=uNam, email=email, joined=now)

#         if not pw:
#             pw = genPw()
#         usr.set_pw(pw)

#         #if( not email_verified):
#             #usr.mark_email_for_activation()
#         #else:
#             #usr.isEmailActivated = True

#         usr.confirmed_at = now
#         usr.roles = ['admin']

#         usr.save()
#         usr._id = usr.id
#         return usr

#     def delete_user(self, user):
#         """Delete the specified user

#         :param user: The user to delete
#         """
#         self.delete(user)
        
# class Struct:
#     def __init__(self, **entries): 
#         self.__dict__.update(entries)
        
# class PyMongoUserDatastore(PyMongoDatastore, UserDatastore):
#     """A PyMongo datastore implementation for Flask-Security that assumes
#     the use of the Flask-MongoEngine extension.
#     """
#     user_db = None
#     def __init__(self, app, user_model, role_model):
#         self.user_model = user_model
#         self.role_model = role_model
        
#         with app.app_context():
#             user_db = db.db
            
#         PyMongoDatastore.__init__(self, user_db)
#         UserDatastore.__init__(self, user_model, role_model)

#     def find_user(self, **kwargs):
#         col = self.db[self.meta['colNam']]
#         usrDict = col.find_one(**kwargs)
#         if usrDict:
#             usr = Struct(**usrDict)
#             return usr
#         else:
#             return None

#     def find_role(self, role):
#         return self.role_model.objects(name=role).first()
