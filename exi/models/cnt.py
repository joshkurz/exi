from flask import current_app
from d import D
from schematics.types import IntType, StringType, FloatType, DateTimeType, EmailType, URLType, BooleanType
from schematics.types.compound import ListType, ModelType
from schematics.types.mongo import ObjectIdType
from bson import ObjectId
from embed import Email, Note, Tel, Im
from . import Role
from . import DMixin
from random import randint, random, Random
import time, hashlib, datetime
from exi.utils.utils import get_hexdigest
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
        