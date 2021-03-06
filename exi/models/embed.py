from schematics.models import Model as _Model
from schematics.types import StringType, IntType, LongType, DateTimeType, EmailType, FloatType, BooleanType, GeoPointType
from schematics.types.compound import ListType, ModelType
from schematics.types.mongo import ObjectIdType
from d import D

class Embs(D):
    '''convenience base for listtype fields, ie, emails, tels, etc'''
    typ     = StringType() 
    '''work'''
    w       = FloatType(description='Sort weight, Sort list by weight value.', default=0)
    prim    = BooleanType(default=False, description='Primary, When multiple emails appear in a list, indicates which is prim. At most one may be prim.')

    meta           = {
        '_c'        : 'Embs',
        }

class LnkTyp(D):
    fam         = BooleanType(description='Is Family Link/Relationship?')
    fr_c        = StringType(description='Fr/Child Document class "_c".')
    frGen       = StringType(description='Fr/Child Gender')
    frNam       = StringType(description='Fr/Child Name/Title')
    frNamS      = StringType(description='Fr/Child Name/Title Short')
    to_c        = StringType(description='To/Parent Document class "_c".')
    toGen       = StringType(description='To/Parent Gender')
    toNam       = StringType(description='To/Parent Name/Title')
    toNamS      = StringType(description='To/Parent Name/Title Short')
    mask        = StringType(description='Sharing Mask')
    '''1, 11, 111, etc used in sh(aring) docs'''

class Lnk(Embs):
    d_c         = StringType(description='Document class "_c".')
    lnkTypDNam  = LongType(description='Link Type Display Name')
    lnkTypDNamS = LongType(description='Link Type Display Name Short')
    dDNam       = LongType(description='Document Display Name')
    sDNamS      = LongType(description='Document Display Name Short')

class Pth(Embs):
    d_c      = StringType(description='Target document class "_c".')
    lnkTypId = LongType(description='Link Type Id.')
    lnkTitle = StringType(description='Link Title.')
    lnkNote  = StringType(description='Link Note.')
    lnks     = ListType(ModelType(Lnk))
    ids      = ListType(LongType())

class Note(Embs):
    title    = StringType()
    note     = StringType()
    noteHTML = StringType()

    def __unicode__(self):
        return self.note

    meta = {
        '_c': 'Note',
        }
    @property
    def vNam(self):
        dNam = self.title
        return dNam

    @property
    def vNamS(self):
        return self.title.lower().replace(' ', '_')


# https://developers.google.com/gdata/docs/2.0/elements#gdMessageKind
class Msg(Embs):
    '''Represents a message, such as an email, a discussion group posting, or a comment.'''
    content = StringType()
    title   = StringType(description='Message subject.')

    meta = {
        '_c': 'Msg',
        }

class Shr(D):
    '''Share'''
    # The reason for this parent field given the fact that Wid'gets can contain an array of other widgets is that OTHER Widgets may LINK to this widget AND add their Share properties. It is necessary
    parId     = ObjectIdType(description='Parent Doc ID, Primary Parent owner of this doc.')
    
    # needed? D has oBy which is owner id
    usrId      = ObjectIdType(description='Usr ID for this Share.')
    
    permission = StringType(description='Permission, a=At and Above, ab=At and below, b=Below.', choices=['a','ab','b'])

    meta = {
        '_c': 'Shr',
        }

class Email(Embs):
    address = EmailType(required=True, description='Email Address')
    note    = StringType(description='note')
    
    meta    = {
        '_c': 'Email',
        }

    @property
    def vNam(self):
        dNam = 'typ_' + self.typ + ': ' + self.address.lower()
        dNam += ' (Primary)' if self.prim else ''
        dNam += (' ' + self.note) if self.note else ''
        return dNam

    @property
    def vNamS(self):
        return (self.typ + ':' + self.address).lower()

class Tel(Embs):
    '''https://developers.google.com/gdata/docs/2.0/elements#gdPhoneNumber'''
    text  = StringType(required=True, description='Human-readable phone number')
    
    uri   = StringType(description='An optional "tel URI", An optional "tel URI" used to represent the number in a formal way, useful for programmatic access, such as a VoIP/PSTN bridge. See RFC 3966 for more information on tel URIs.')
    note  = StringType(description='note')
    
    meta  = {
        '_c': 'Tel',
        }

    @property
    def vNam(self):
        s = ('typ_' + self.typ + ': ') if self.typ else ''
        s = self.text.lower()
        s += ' (Primary)' if self.prim else ''
        s += (' ' + self.note) if self.note else ''
        return s

    @property
    def vNamS(self):
        s = (self.typ + ':') if self.typ else ''
        s += self.text.lower()
        s += ' (Primary)' if self.prim else ''
        return s.lower().replace('() -_', '')

class Im(Embs):
    '''https://developers.google.com/gdata/docs/2.0/elements#gdIm'''
    address  = StringType(required=True, description='IM Address')
    
    protocol = StringType(required=True, description='IM network, Identifies the IM network. The value may be either one of the standard values (shown below) or a URI identifying a proprietary IM network.')
    '''['aim','msn','yahoo','skype','qq','gtalk','icq','jabber']'''
    
    note  = StringType(description='note')

    meta = {
        '_c': 'Im',
        }

    @property
    def vNam(self):
        s = ''
        s += ('typ_' + self.typ + ': ') if self.typ else ''
        s += self.address.lower()
        s += ' (Primary)' if self.prim else ''
        s += (' ' + self.note) if self.note else ''
        return s

    @property
    def vNamS(self):
        s = ''
        s += (self.typ + ':') if self.typ else ''
        s += self.protocol.lower() + ':' + self.address.lower()
        s += ' (Primary)' if self.prim else ''
        return s.lower().replace(' ', '_')

class Rating(D):
    eId       = IntType(description='Element Id')
    avg       = FloatType(description='Average rating.')
    max       = IntType(description='The rating scale\'s maximum value.')
    min       = IntType(description='The rating scale\'s minimum value.')
    numRaters = IntType(description='Number of ratings taken into account when computing the average value.')
    rel       = StringType(description='Specifies the aspect that\'s being rated. If not specified, the rating is an overall rating.')
    val       = IntType(description='Rating value.')

class PlAspectRating(_Model):
    typ       = StringType(description='Type, The name of the aspect that is being rated. eg. atmosphere, service, food, overall, etc.')
    # rating    = Rating(description='Rating, The user\'s rating for this particular aspect')

    meta = {
        '_c': 'PlAspectRate',
        }

class Review(Embs):
    '''https://developers.google.com/maps/documentation/javascript/places#place_details_responses'''
    aspects = ListType(ModelType(PlAspectRating))
    body    = StringType(description='the user\'s review.')

    meta = {
        '_c': 'Review',
        }
