from d import D
from schematics.types import StringType

class Role(D):
    name        = StringType(description='')
    description = StringType(description='')
    
    meta        = {
        'collNam': 'roles',
        '_c': 'Role',
        }