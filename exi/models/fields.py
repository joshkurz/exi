from schematics.types import BaseType


DEFAULT_CONNECTION_NAME = 'default'

class SequenceType(BaseType):
    """Provides a sequental counter
    """

    def __init__(self, *args, **kwargs):
        self.countersColNam = 'col.counters'
        return super(SequenceType, self).__init__(*args, **kwargs)
    
    def generate_new_value(self, db):
        """
        Generate and Increment the counter
        """
        counter = db[self.countersColNam].find_and_modify(query={"_id": self.colNam},
                                             update={"$inc": {"next": 1}},
                                             new=True,
                                             upsert=True)
        return counter['next']
    
    def __get__(self, instance, owner):
        """Descriptor for retrieving a value from a field in a model. Do
        any necessary conversion between Python and `Structures` types.
        """
        if instance is None:
            # Model class being used rather than a model object
            return self

        value = instance._data.get(self.field_name)

        if value is None:
            self.colNam = instance.meta['collNam']
            value = self.generate_new_value()
            # Callable values are best for mutable defaults
            if callable(value):
                value = value()
        return value

    def __set__(self, instance, value):
        if value is None and instance._initialised:
            value = self.generate_new_value()
        instance._data[self.field_name] = value
        super(SequenceType, self).__set__(instance, value)

    def _jsonschema_type(self):
        return 'string'

    def validate(self, value):
        """Make sure the value is a valid uuid representation.  See
        http://docs.python.org/library/uuid.html for accepted formats.
        """
        new_value = value
        
        if not isinstance(value, (uuid.UUID,)):
            try:
                new_value = uuid.UUID(value)
            except ValueError:
                error_msg = 'Not a valid UUID value'
                return FieldResult(ERROR_FIELD_TYPE_CHECK, error_msg,
                                   self.field_name, value)

        return FieldResult(OK, 'success', self.field_name, new_value)

    def for_json(self, value):
        """Return a JSON safe version of the UUID object.
        """

        return str(value)

