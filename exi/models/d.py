from schematics.models import Model
from schematics.types import StringType, IntType, LongType, DateTimeType, BooleanType
from schematics.types.mongo import ObjectIdType
from schematics.types.compound import ModelType
from exi.db import db
from exi.utils.name import slug
import re

class D(Model):
    colNam = 'd'
    def commit(self):
        pass

    def put(self, model):
        raise NotImplementedError
    
    _c             = StringType(required=True, description='Class')
    sId            = LongType()

    # unique slug value generated on save and optionally used for SEO friendly urls.
    slug           = StringType(description='Unique Slug')
    
    meta           = {
        'colNam': 'd',
        '_c'        : 'D',
        }

    @classmethod
    def find_one(cls, query=None, fields=None):
        """Returns a doc matching the provided paramters."""
        return db[cls.colNam].find_one(spec_or_id=query, fields=fields)
        #doc = db[cls.colNam].find_one(spec_or_id=query, fields=fields)
        #if doc:
            #return cls(**doc)

    @classmethod
    def delete(cls, query):
        """Remove matching docs."""
        return db[cls.colNam].remove(query)

    def generate_slug(self, value):
        col = db[self.meta['colNam']]
        slugVal = slug(value)
        slug_regex = '^%s' % slugVal
        existing_docs = [
            {'_id': doc['_id'], 'slug': doc['slug']} for doc in
            col.find({'slug': {'$regex':slug_regex}})
        ]
        matches = [int(re.search(r'-[\d]+$', doc['slug']).group()[-1:])
            for doc in existing_docs if re.search(r'-[\d]+$', doc['slug'])]

        # Four scenarios:
        # (1) No match is found, this is a brand new slug
        # (2) A matching document is found, but it's this one
        # (3) A matching document is found but without any number
        # (4) A matching document is found with an incrementing value
        next = 1
        if len(existing_docs) == 0:
            return slugVal
        elif hasattr(self, '_id') and self._id in [doc['id'] for doc in existing_docs]:
            return self['slug']
        elif not matches:
            return u'%s-%s' % (slugVal, next)
        else:
            next = max(matches) + 1
            return u'%s-%s' % (slugVal, next)

    
    
    
    def save(self):
        colNam = self.meta['colNam']
        col = db[colNam]
        
        # convenient class name
        if not self._c:
            self._c = self._class_name.split('.')[-1]

        # generate a sequence sId 
        if not self.sId:
            counter = db['col.counters'].find_and_modify(query={"id": colNam},
                        update={"$inc": {"next": 1}}, new=True, upsert=True)
            self.sId = counter['next']

        # we want to generate a slug and make sure whatever slug may have been
        # given, if any, will be unique
        if self.slug:
            slugDefault = self.slug
        else:
            try:
                slugDefault = self.vNam
            except:
                slugDefault = ''
                
        self.slug = self.generate_slug(slugDefault) 
        
        d = dict([(k,v) for k,v in self.to_python().iteritems() if v])
        
        if hasattr(self, 'id') and self.id:
            d['id'] = d['_id'] = self.id
            
        id = col.save(d)
        if id: self.id = id
        return id